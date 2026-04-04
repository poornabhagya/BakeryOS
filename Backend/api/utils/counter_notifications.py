from django.db import transaction
from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from decimal import Decimal

from api.models import CounterSession, Notification, NotificationReceipt, Sale, User


COUNTER_ACTIONS = {"opened", "closed"}
TARGET_ROLES = ["Manager", "Cashier"]


def _currency(amount: Decimal) -> str:
    return f"{(amount or Decimal('0')).quantize(Decimal('0.01'))}"


def _format_session_summary(*, session: CounterSession, actor: User) -> str:
    actor_name = actor.full_name or actor.username
    opened_name = session.opened_by.full_name or session.opened_by.username

    sales = Sale.objects.filter(
        date_time__gte=session.opened_at,
        date_time__lte=session.closed_at,
    )

    total_revenue = sales.aggregate(
        total=Coalesce(Sum('total_amount'), Decimal('0')),
    )['total'] or Decimal('0')
    total_transactions = sales.count()

    cash_total = sales.filter(payment_method='Cash').aggregate(
        total=Coalesce(Sum('total_amount'), Decimal('0')),
    )['total'] or Decimal('0')
    card_total = sales.filter(payment_method='Card').aggregate(
        total=Coalesce(Sum('total_amount'), Decimal('0')),
    )['total'] or Decimal('0')

    opened_local = timezone.localtime(session.opened_at).strftime('%Y-%m-%d %I:%M %p')
    closed_local = timezone.localtime(session.closed_at).strftime('%Y-%m-%d %I:%M %p')

    return (
        "SHIFT SUMMARY REPORT\n"
        "--------------------\n"
        f"Opened: {opened_local} by {opened_name}\n"
        f"Closed: {closed_local} by {actor_name}\n"
        "\n"
        f"Total Sales: Rs. {_currency(total_revenue)}\n"
        f"Transactions: {total_transactions}\n"
        f"Cash Sales: Rs. {_currency(cash_total)}\n"
        f"Card Sales: Rs. {_currency(card_total)}\n"
        "--------------------\n"
        "Status: Counter Successfully Closed."
    )


def create_counter_status_notification(*, actor: User, action: str) -> Notification:
    """Create a counter open/close notification and fan it out to manager/cashier users."""
    normalized_action = (action or "").strip().lower()
    if normalized_action not in COUNTER_ACTIONS:
        raise ValueError("Invalid action. Expected 'opened' or 'closed'.")

    actor_name = actor.full_name or actor.username
    actor_role = getattr(actor, "role", None) or "Unknown"
    now = timezone.now()
    session = None

    if normalized_action == 'opened':
        session = CounterSession.objects.create(
            opened_at=now,
            opened_by=actor,
            is_active=True,
        )
        opened_at = timezone.localtime(now).strftime('%Y-%m-%d %I:%M %p')
        message = f"Counter opened by {actor_name} ({actor_role}) on {opened_at}."
    else:
        session = CounterSession.objects.filter(is_active=True).order_by('-opened_at').first()
        if session is None:
            raise ValueError('No active counter session found to close.')

        session.closed_at = now
        session.closed_by = actor
        session.is_active = False
        session.save(update_fields=['closed_at', 'closed_by', 'is_active', 'updated_at'])
        message = _format_session_summary(session=session, actor=actor)

    recipients = User.objects.filter(
        is_active=True,
        status="active",
    ).filter(
        Q(role__in=TARGET_ROLES) | Q(groups__name__in=TARGET_ROLES)
    ).distinct()

    with transaction.atomic():
        notification = Notification.objects.create(
            title="Counter Status Update",
            message=message,
            type="System",
            counter_session=session,
            icon="info",
        )

        NotificationReceipt.objects.bulk_create(
            [
                NotificationReceipt(notification=notification, user=user)
                for user in recipients
            ]
        )

    return notification
