"""
Query Optimization Utilities for BakeryOS Backend

Provides decorators and utilities for:
- Automatic select_related optimization
- Automatic prefetch_related optimization
- Caching frequently accessed data
- Query count monitoring
"""

from functools import wraps
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# QUERY OPTIMIZATION FOR VIEWSETS
# ============================================================================

class OptimizedQueryMixin:
    """
    Mixin to add optimized query patterns to ViewSets.
    
    Usage:
    class ProductViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
        optimized_relations = {
            'list': {
                'select_related': ['category'],
                'prefetch_related': ['batches', 'wastage_records'],
            },
            'retrieve': {
                'select_related': ['category'],
                'prefetch_related': ['batches', 'recipes', 'stock_history'],
            }
        }
    """
    
    optimized_relations = {}
    
    def get_queryset(self):
        """Override get_queryset to apply optimizations"""
        queryset = super().get_queryset()
        
        # Check if optimizations exist for current action
        if self.action not in self.optimized_relations:
            return queryset
        
        optimization = self.optimized_relations[self.action]
        
        # Apply select_related
        if 'select_related' in optimization:
            for relation in optimization['select_related']:
                queryset = queryset.select_related(relation)
        
        # Apply prefetch_related
        if 'prefetch_related' in optimization:
            from django.db.models import Prefetch
            for relation in optimization['prefetch_related']:
                if isinstance(relation, Prefetch):
                    queryset = queryset.prefetch_related(relation)
                else:
                    queryset = queryset.prefetch_related(relation)
        
        return queryset


# ============================================================================
# CACHING DECORATORS FOR CUSTOM ACTIONS
# ============================================================================

def cache_list_endpoint(timeout=300):
    """
    Decorator to cache list endpoint results.
    
    Args:
        timeout: Cache timeout in seconds (default: 300 = 5 minutes)
    
    Usage:
        @cache_list_endpoint(timeout=600)
        @action(detail=False, methods=['get'])
        def active_discounts(self, request):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Generate cache key based on view, filters, and pagination
            cache_key = f"{self.__class__.__name__}:{func.__name__}:{request.GET.urlencode()}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result:
                logger.debug(f"Cache hit for {cache_key}")
                return result
            
            # Execute function
            result = func(self, request, *args, **kwargs)
            
            # Cache the response
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cached {cache_key} for {timeout}s")
            
            return result
        return wrapper
    return decorator


def cache_analytics_endpoint(timeout=3600):
    """
    Decorator to cache analytics endpoint results (longer timeout).
    
    Args:
        timeout: Cache timeout in seconds (default: 3600 = 1 hour)
    
    Usage:
        @cache_analytics_endpoint()
        @action(detail=False, methods=['get'])
        def daily_analytics(self, request):
            ...
    """
    return cache_list_endpoint(timeout=timeout)


def cache_dashboard_endpoint(timeout=900):
    """
    Decorator to cache dashboard endpoint results.
    
    Args:
        timeout: Cache timeout in seconds (default: 900 = 15 minutes)
    
    Usage:
        @cache_dashboard_endpoint()
        @action(detail=False, methods=['get'])
        def kpis(self, request):
            ...
    """
    return cache_list_endpoint(timeout=timeout)


# ============================================================================
# QUERY COUNT MONITORING
# ============================================================================

class QueryCounterMixin:
    """
    Mixin to log query counts for performance monitoring.
    
    Usage:
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        
        # In class-based view or test
        with CaptureQueriesContext(connection) as captured:
            response = view(request)
        
        logger.info(f"Executed {len(captured)} queries")
    """
    
    @staticmethod
    def log_query_count(operation_name):
        """Log the number of database queries executed"""
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with CaptureQueriesContext(connection) as captured:
                    result = func(*args, **kwargs)
                
                query_count = len(captured)
                if query_count > 10:
                    logger.warning(
                        f"{operation_name}: Executed {query_count} queries "
                        "(consider optimizing with select_related/prefetch_related)"
                    )
                else:
                    logger.info(f"{operation_name}: Executed {query_count} queries")
                
                return result
            return wrapper
        return decorator


# ============================================================================
# PAGINATION HELPERS
# ============================================================================

class StandardPagination:
    """Standard pagination settings for list endpoints"""
    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    PAGE_SIZE_QUERY_PARAM = 'page_size'


class LargePagination:
    """Larger pagination for analytics endpoints"""
    PAGE_SIZE = 50
    MAX_PAGE_SIZE = 500
    PAGE_SIZE_QUERY_PARAM = 'page_size'


class SmallPagination:
    """Smaller pagination for dropdown/select endpoints"""
    PAGE_SIZE = 10
    MAX_PAGE_SIZE = 50
    PAGE_SIZE_QUERY_PARAM = 'page_size'


# ============================================================================
# CACHE INVALIDATION UTILITIES
# ============================================================================

def invalidate_cache_pattern(pattern_prefix):
    """
    Invalidate all cache keys matching a pattern.
    
    Note: LocMemCache doesn't support pattern deletion, so this is 
    a placeholder for future Redis implementation.
    
    Args:
        pattern_prefix: Prefix of cache keys to invalidate
    
    Usage:
        invalidate_cache_pattern('ProductViewSet')
    """
    logger.info(f"Cache invalidation pattern: {pattern_prefix}")
    # TODO: Implement with Redis when scaling
    pass


def invalidate_product_cache():
    """Invalidate all product-related caches"""
    invalidate_cache_pattern('ProductViewSet')


def invalidate_sales_cache():
    """Invalidate all sales-related caches"""
    invalidate_cache_pattern('SaleViewSet')


def invalidate_analytics_cache():
    """Invalidate all analytics caches"""
    invalidate_cache_pattern('AnalyticsViewSet')


# ============================================================================
# QUERY OPTIMIZATION PROFILES
# ============================================================================

OPTIMIZED_PROFILES = {
    'category': {
        'select_related': [],
        'prefetch_related': []
    },
    'product': {
        'select_related': ['category'],
        'prefetch_related': ['batches', 'recipes', 'stock_history']
    },
    'ingredient': {
        'select_related': ['category'],
        'prefetch_related': ['batches', 'stock_history']
    },
    'sale': {
        'select_related': ['cashier', 'discount'],
        'prefetch_related': ['items', 'items__product']
    },
    'product_batch': {
        'select_related': ['product'],
        'prefetch_related': ['stock_history']
    },
    'ingredient_batch': {
        'select_related': ['ingredient'],
        'prefetch_related': ['stock_history']
    },
    'user': {
        'select_related': [],
        'prefetch_related': []
    },
}


def apply_optimization_profile(queryset, model_name, action='list'):
    """
    Apply pre-defined optimization profile to a queryset.
    
    Args:
        queryset: Django queryset to optimize
        model_name: Name of model (e.g., 'product', 'sale')
        action: Action name ('list', 'retrieve', etc.)
    
    Returns:
        Optimized queryset
    
    Usage:
        queryset = Product.objects.all()
        queryset = apply_optimization_profile(queryset, 'product', 'list')
    """
    if model_name not in OPTIMIZED_PROFILES:
        return queryset
    
    profile = OPTIMIZED_PROFILES[model_name]
    
    # Apply select_related
    for relation in profile.get('select_related', []):
        queryset = queryset.select_related(relation)
    
    # Apply prefetch_related
    for relation in profile.get('prefetch_related', []):
        queryset = queryset.prefetch_related(relation)
    
    return queryset
