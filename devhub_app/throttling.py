from django.conf import settings
from django.core.cache import cache
from ipware import get_client_ip
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
    client_ip, is_routable = get_client_ip(
        request,
        request_header_order=["X-Forwarded-For", "X-Real-IP", "REMOTE_ADDR"],
    )
    if client_ip is None:
        client_ip = "unknown"
    cache_key = f"rate-limit:{key_prefix}:{client_ip}"
    current = cache.get(cache_key, 0)
    if current >= limit:
        return False
    cache.set(cache_key, current + 1, timeout=window_seconds)
    return True
