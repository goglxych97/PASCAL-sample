# cache_utils.py
from functools import lru_cache, wraps

def slice_cache(maxsize=100):
    """
    Decorator to create a cache for each slice.
    """
    def decorator(func):
        cache = lru_cache(maxsize=maxsize)(func)

        @wraps(func)
        def wrapper(self, slice_index, *args):
            return cache(self, slice_index, *args)
        wrapper.cache_clear = cache.cache_clear

        def cache_invalidate(slice_index):
            key = (self, slice_index) + args
            if key in cache.cache:
                del cache.cache[key]
        wrapper.cache_invalidate = cache_invalidate
        
        return wrapper

    return decorator
