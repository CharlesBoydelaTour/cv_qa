# ratelimit_middleware.py

from django.core.cache import cache
from django.http import JsonResponse


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/ask/" and request.method == "POST":
            ip = request.META.get("REMOTE_ADDR")
            key = f"ratelimit:{ip}"
            count = cache.get(key, 0)
            if count >= 5:
                return JsonResponse(
                    {
                        "error": "Too many requests",
                        "message": "You have exceeded the limit of 5 requests per minute. Please wait a minute before trying again.",
                    },
                    status=429,
                )
            else:
                cache.set(
                    key, count + 1, 60
                )  # Increment count and set 1-minute expiration
        response = self.get_response(request)
        return response
