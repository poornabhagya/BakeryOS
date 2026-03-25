"""
Script to seed WastageReason data into the database.

Run with: python manage.py shell < seed_wastage_reasons.py
Or from manage.py:
    from django.core.management import call_command
    exec(open('api/scripts/seed_wastage_reasons.py').read())
"""

from api.models import WastageReason

# Predefined wastage reasons
WASTAGE_REASONS_DATA = [
    {
        'reason': 'Expired',
        'description': 'Products that have passed their expiration date'
    },
    {
        'reason': 'Damaged',
        'description': 'Products that are physically damaged or broken'
    },
    {
        'reason': 'Spilled',
        'description': 'Products that were accidentally spilled or lost'
    },
    {
        'reason': 'Theft',
        'description': 'Products lost due to theft or unauthorized removal'
    },
    {
        'reason': 'Spoiled',
        'description': 'Products that have spoiled due to improper storage'
    },
    {
        'reason': 'Pest Damage',
        'description': 'Products damaged by insects, rodents, or other pests'
    },
    {
        'reason': 'Burn',
        'description': 'Products burned or overcooked during production'
    },
    {
        'reason': 'Other',
        'description': 'Other wastage reasons not listed above'
    },
]


def seed_wastage_reasons():
    """
    Create wastage reason records in the database.
    Skips if reason already exists.
    """
    created_count = 0
    skipped_count = 0

    for reason_data in WASTAGE_REASONS_DATA:
        # Check if reason already exists
        if WastageReason.objects.filter(reason=reason_data['reason']).exists():
            print(f"✓ Skipped: '{reason_data['reason']}' (already exists)")
            skipped_count += 1
            continue

        # Create the reason
        reason = WastageReason.objects.create(
            reason=reason_data['reason'],
            description=reason_data['description']
        )
        print(f"✓ Created: {reason.reason_id} - {reason.reason}")
        created_count += 1

    print(f"\n{'='*50}")
    print(f"Summary:")
    print(f"  Created: {created_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Total:   {created_count + skipped_count}")
    print(f"{'='*50}")

    return created_count, skipped_count


if __name__ == '__main__':
    seed_wastage_reasons()
