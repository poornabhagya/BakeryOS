from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta

from api.models import IngredientWastage, Ingredient, WastageReason, User
from api.serializers import (
    IngredientWastageListSerializer,
    IngredientWastageDetailSerializer,
    IngredientWastageCreateSerializer,
)


class IngredientWastageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ingredient wastage management.
    
    Endpoints:
    - GET /api/ingredient-wastages/ - List all wastages
    - POST /api/ingredient-wastages/ - Create new wastage (Storekeeper)
    - GET /api/ingredient-wastages/{id}/ - Get wastage details
    - DELETE /api/ingredient-wastages/{id}/ - Delete wastage (Manager only)
    - GET /api/ingredient-wastages/analytics/ - Wastage analytics
    """
    
    queryset = IngredientWastage.objects.select_related(
        'ingredient_id',
        'batch_id',
        'reason_id',
        'reported_by'
    ).all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return IngredientWastageCreateSerializer
        elif self.action == 'retrieve':
            return IngredientWastageDetailSerializer
        return IngredientWastageListSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'destroy':
            # Only Manager can delete
            from rest_framework.permissions import IsAuthenticated
            # Will be checked in destroy method
            pass
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        """
        List all wastages with optional filters.
        
        Query parameters:
        - ingredient_id: Filter by ingredient
        - batch_id: Filter by batch
        - reason_id: Filter by reason
        - reported_by: Filter by reporter
        - date_from: Filter by start date (YYYY-MM-DD)
        - date_to: Filter by end date (YYYY-MM-DD)
        - min_loss: Filter by minimum loss amount
        """
        queryset = self.get_queryset()
        
        # Apply filters
        ingredient_id = request.query_params.get('ingredient_id')
        if ingredient_id:
            queryset = queryset.filter(ingredient_id=ingredient_id)
        
        batch_id = request.query_params.get('batch_id')
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        
        reason_id = request.query_params.get('reason_id')
        if reason_id:
            queryset = queryset.filter(reason_id=reason_id)
        
        reported_by = request.query_params.get('reported_by')
        if reported_by:
            queryset = queryset.filter(reported_by=reported_by)
        
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        min_loss = request.query_params.get('min_loss')
        if min_loss:
            queryset = queryset.filter(total_loss__gte=float(min_loss))
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new ingredient wastage record.
        Only Storekeeper and Manager can create.
        """
        # Check permission
        user = request.user
        if user.role not in ['Storekeeper', 'Manager']:
            return Response(
                {'detail': 'Only Storekeeper or Manager can report ingredient wastage.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Set reported_by to current user if not provided
        data = request.data.copy()
        if 'reported_by' not in data or not data['reported_by']:
            data['reported_by'] = user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return detail serializer in response
        detail_serializer = IngredientWastageDetailSerializer(serializer.instance)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve wastage details."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete/undo wastage record.
        Only Manager can delete.
        Restores ingredient quantity.
        """
        user = request.user
        if user.role != 'Manager':
            return Response(
                {'detail': 'Only Manager can delete wastage records.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance = self.get_object()
        
        # Restore ingredient quantity
        ingredient = instance.ingredient_id
        ingredient.total_quantity += instance.quantity
        ingredient.save()
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get wastage analytics.
        
        Returns:
        - Total wastage amount
        - Wastage by reason
        - Wastage by ingredient
        - Daily wastage trend
        """
        queryset = self.get_queryset()
        
        # Apply optional date filters
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Total wastage
        total_loss = queryset.aggregate(Sum('total_loss'))['total_loss__sum'] or 0
        total_quantity = queryset.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_count = queryset.count()
        
        # Wastage by reason
        by_reason = queryset.values('reason_id__reason').annotate(
            count=Count('id'),
            total_loss=Sum('total_loss'),
            total_quantity=Sum('quantity')
        ).order_by('-total_loss')
        
        # Wastage by ingredient
        by_ingredient = queryset.values('ingredient_id__name').annotate(
            count=Count('id'),
            total_loss=Sum('total_loss'),
            total_quantity=Sum('quantity')
        ).order_by('-total_loss')[:10]  # Top 10
        
        # Daily trend (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_trend = queryset.filter(
            created_at__gte=thirty_days_ago
        ).values('created_at__date').annotate(
            total_loss=Sum('total_loss'),
            count=Count('id')
        ).order_by('created_at__date')
        
        return Response({
            'summary': {
                'total_loss': float(total_loss),
                'total_quantity': float(total_quantity),
                'total_records': total_count,
            },
            'by_reason': list(by_reason),
            'by_ingredient': list(by_ingredient),
            'daily_trend': list(daily_trend),
        })
    
    @action(detail=False, methods=['get'], url_path='ingredient/(?P<ingredient_id>[^/.]+)/history')
    def ingredient_history(self, request, ingredient_id=None):
        """
        Get wastage history for a specific ingredient.
        
        Parameters:
        - ingredient_id: Ingredient ID
        """
        try:
            ingredient = Ingredient.objects.get(id=ingredient_id)
        except Ingredient.DoesNotExist:
            return Response(
                {'detail': 'Ingredient not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        wastages = self.get_queryset().filter(ingredient_id=ingredient_id)
        
        # Apply pagination
        page = self.paginate_queryset(wastages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(wastages, many=True)
        return Response(serializer.data)
