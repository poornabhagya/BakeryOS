from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from datetime import timedelta

from api.models import ProductWastage, IngredientWastage, WastageReason
from api.serializers import (
    ProductWastageListSerializer,
    IngredientWastageListSerializer,
)
from api.permissions import IsManager


class WastageViewSet(viewsets.ModelViewSet):
    """
    Combined ViewSet for both product and ingredient wastage management.
    
    Returns a combined list of both product and ingredient wastages.
    
    Endpoints:
    - GET /api/wastage/ - List all wastages (both product and ingredient)
    - GET /api/wastage/{id}/ - Get wastage details (based on wastage_id)
    - GET /api/wastage/analytics/ - Wastage analytics
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return combined queryset of both product and ingredient wastages.
        Uses union to combine both querysets.
        """
        # Get product wastages
        product_wastages = ProductWastage.objects.select_related(
            'product_id',
            'reason_id',
            'reported_by'
        ).values(
            'id',
            'wastage_id',
            'quantity',
            'unit_cost',
            'total_loss',
            'notes',
            'created_at',
            'updated_at',
            product_name=F('product_id__name'),
            category_name=F('product_id__category_id__name'),
            reason_desc=F('reason_id__description'),
            reported_by_name=F('reported_by__full_name'),
            reported_by_username=F('reported_by__username'),
            wastage_type=F('id')  # Placeholder for type
        ).annotate(wastage_type_label='Product').order_by('-created_at')

        # Get ingredient wastages
        ingredient_wastages = IngredientWastage.objects.select_related(
            'ingredient_id',
            'reason_id',
            'reported_by'
        ).values(
            'id',
            'wastage_id',
            'quantity',
            'unit_cost',
            'total_loss',
            'notes',
            'created_at',
            'updated_at',
            product_name=F('ingredient_id__name'),
            category_name=F('ingredient_id__category_id__name'),
            reason_desc=F('reason_id__description'),
            reported_by_name=F('reported_by__full_name'),
            reported_by_username=F('reported_by__username'),
            wastage_type=F('id')  # Placeholder for type
        ).annotate(wastage_type_label='Ingredient').order_by('-created_at')

        # Combine using union and order by created_at
        combined = product_wastages.union(ingredient_wastages, all=True)
        return combined
    
    def list(self, request, *args, **kwargs):
        """
        List all wastages (both product and ingredient) with optional filters.
        
        Query parameters:
        - reason_id: Filter by reason
        - reported_by: Filter by reporter
        - date_from: Filter by start date (YYYY-MM-DD)
        - date_to: Filter by end date (YYYY-MM-DD)
        - min_loss: Filter by minimum loss amount
        - type: Filter by wastage type ('Product' or 'Ingredient')
        """
        # Get both querysets and combine
        product_wastages = ProductWastage.objects.select_related(
            'product_id',
            'reason_id',
            'reported_by'
        ).all()

        ingredient_wastages = IngredientWastage.objects.select_related(
            'ingredient_id',
            'reason_id',
            'reported_by'
        ).all()

        # Apply filters to product wastages
        reason_id = request.query_params.get('reason_id')
        if reason_id:
            product_wastages = product_wastages.filter(reason_id=reason_id)
            ingredient_wastages = ingredient_wastages.filter(reason_id=reason_id)

        reported_by = request.query_params.get('reported_by')
        if reported_by:
            product_wastages = product_wastages.filter(reported_by=reported_by)
            ingredient_wastages = ingredient_wastages.filter(reported_by=reported_by)

        date_from = request.query_params.get('date_from')
        if date_from:
            product_wastages = product_wastages.filter(created_at__gte=date_from)
            ingredient_wastages = ingredient_wastages.filter(created_at__gte=date_from)

        date_to = request.query_params.get('date_to')
        if date_to:
            product_wastages = product_wastages.filter(created_at__lte=date_to)
            ingredient_wastages = ingredient_wastages.filter(created_at__lte=date_to)

        min_loss = request.query_params.get('min_loss')
        if min_loss:
            try:
                min_loss_float = float(min_loss)
                product_wastages = product_wastages.filter(total_loss__gte=min_loss_float)
                ingredient_wastages = ingredient_wastages.filter(total_loss__gte=min_loss_float)
            except (ValueError, TypeError):
                pass

        wastage_type = request.query_params.get('type')
        if wastage_type == 'Product':
            combined_wastages = list(product_wastages)
            ingredient_wastages = IngredientWastage.objects.none()
        elif wastage_type == 'Ingredient':
            ingredient_wastages = list(ingredient_wastages)
            product_wastages = ProductWastage.objects.none()
        else:
            combined_wastages = list(product_wastages) + list(ingredient_wastages)

        # Sort by created_at descending
        if isinstance(combined_wastages, list):
            combined_wastages.sort(key=lambda x: x.created_at, reverse=True)
        else:
            combined_wastages = sorted(
                list(product_wastages) + list(ingredient_wastages),
                key=lambda x: x.created_at,
                reverse=True
            )

        # Paginate
        page = self.paginate_queryset(combined_wastages)
        if page is not None:
            serialized_product = ProductWastageListSerializer(
                [w for w in page if isinstance(w, ProductWastage)],
                many=True
            ).data
            serialized_ingredient = IngredientWastageListSerializer(
                [w for w in page if isinstance(w, IngredientWastage)],
                many=True
            ).data

            combined_data = serialized_product + serialized_ingredient
            return self.get_paginated_response(combined_data)

        serialized_product = ProductWastageListSerializer(
            [w for w in combined_wastages if isinstance(w, ProductWastage)],
            many=True
        ).data
        serialized_ingredient = IngredientWastageListSerializer(
            [w for w in combined_wastages if isinstance(w, IngredientWastage)],
            many=True
        ).data

        combined_data = serialized_product + serialized_ingredient
        return Response(combined_data)

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get wastage analytics (both product and ingredient).
        """
        date_range_days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=date_range_days)

        product_stats = ProductWastage.objects.filter(
            created_at__gte=start_date
        ).aggregate(
            total_wastages=Count('id'),
            total_loss=Sum('total_loss'),
            total_quantity=Sum('quantity')
        )

        ingredient_stats = IngredientWastage.objects.filter(
            created_at__gte=start_date
        ).aggregate(
            total_wastages=Count('id'),
            total_loss=Sum('total_loss'),
            total_quantity=Sum('quantity')
        )

        # Combine stats
        combined_stats = {
            'total_product_wastages': product_stats['total_wastages'] or 0,
            'total_product_loss': float(product_stats['total_loss'] or 0),
            'total_product_quantity': float(product_stats['total_quantity'] or 0),
            'total_ingredient_wastages': ingredient_stats['total_wastages'] or 0,
            'total_ingredient_loss': float(ingredient_stats['total_loss'] or 0),
            'total_ingredient_quantity': float(ingredient_stats['total_quantity'] or 0),
            'total_wastages': (product_stats['total_wastages'] or 0) + (ingredient_stats['total_wastages'] or 0),
            'total_loss': float((product_stats['total_loss'] or 0) + (ingredient_stats['total_loss'] or 0)),
            'date_range_days': date_range_days,
        }

        return Response(combined_stats)

    @action(detail=False, methods=['get'])
    def top_reasons(self, request):
        """
        Get top wastage reasons (both product and ingredient combined).
        """
        limit = int(request.query_params.get('limit', 5))
        date_range_days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=date_range_days)

        product_reasons = ProductWastage.objects.filter(
            created_at__gte=start_date
        ).values('reason_id__description').annotate(
            count=Count('id'),
            total_loss=Sum('total_loss'),
            type='Product'
        )

        ingredient_reasons = IngredientWastage.objects.filter(
            created_at__gte=start_date
        ).values('reason_id__description').annotate(
            count=Count('id'),
            total_loss=Sum('total_loss'),
            type='Ingredient'
        )

        # Combine by reason
        reasons_dict = {}
        for reason_data in product_reasons:
            reason = reason_data['reason_id__description']
            if reason not in reasons_dict:
                reasons_dict[reason] = {'count': 0, 'total_loss': 0, 'types': []}
            reasons_dict[reason]['count'] += reason_data['count']
            reasons_dict[reason]['total_loss'] += reason_data['total_loss']
            if 'Product' not in reasons_dict[reason]['types']:
                reasons_dict[reason]['types'].append('Product')

        for reason_data in ingredient_reasons:
            reason = reason_data['reason_id__description']
            if reason not in reasons_dict:
                reasons_dict[reason] = {'count': 0, 'total_loss': 0, 'types': []}
            reasons_dict[reason]['count'] += reason_data['count']
            reasons_dict[reason]['total_loss'] += reason_data['total_loss']
            if 'Ingredient' not in reasons_dict[reason]['types']:
                reasons_dict[reason]['types'].append('Ingredient')

        # Sort by count descending
        sorted_reasons = sorted(
            reasons_dict.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:limit]

        result = [
            {
                'reason': reason,
                'count': data['count'],
                'total_loss': float(data['total_loss']),
                'types': data['types']
            }
            for reason, data in sorted_reasons
        ]

        return Response(result)
