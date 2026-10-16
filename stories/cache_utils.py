import logging

from django.core.cache import cache
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


def safe_cache_get(key):
    try:
        return cache.get(key)
    except RedisError:
        logger.warning("Redis cache read failed")
        return None


def safe_cache_set(key, value, timeout=300):
    try:
        cache.set(key, value, timeout=timeout)
    except RedisError:
        logger.warning("Redis cache write failed")


def safe_cache_delete(key):
    try:
        cache.delete(key)
    except RedisError:
        logger.warning("Redis cache invalidation failed")