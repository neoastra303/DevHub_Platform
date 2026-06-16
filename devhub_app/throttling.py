from django.conf import settings
from django.core.cache import cache
from rest_framework.throttling import UserRateThrottle


class ConfigurableUserRateThrottle(UserRateThrottle):
    settings_name = None
    fallback_rate = None

    def get_rate(self):
        if self.settings_name:
            return getattr(settings, self.settings_name, self.fallback_rate)
        return self.fallback_rate


class ApiWriteThrottle(ConfigurableUserRateThrottle):
    scope = "api_write"
    settings_name = "DEVHUB_API_WRITE_RATE"
    fallback_rate = "30/hour"


class ApiBurstThrottle(ConfigurableUserRateThrottle):
    scope = "api_burst"
    settings_name = "DEVHUB_API_BURST_RATE"
    fallback_rate = "120/hour"


def check_ip_rate_limit(request, key_prefix, limit, window_seconds):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR", "unknown")
    cache_key = f"rate-limit:{key_prefix}:{ip_address}"

    # Atomic first-access check
    if cache.add(cache_key, 1, timeout=window_seconds):
        return True

    # Atomic increment (Redis); fallback for LocMemCache
    try:
        current = cache.incr(cache_key)
    except (ValueError, NotImplementedError):
        current = cache.get(cache_key, 0)

    return current <= limit
