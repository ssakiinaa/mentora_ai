"""
Custom middleware to handle HTTPS issues in development
"""
from django.http import HttpResponseBadRequest


class DisableHTTPSMiddleware:
    """
    Middleware to prevent HTTPS connections in development.
    This helps when browsers try to force HTTPS on localhost.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if request is trying to use HTTPS in development
        if request.scheme == 'https' and not request.is_secure():
            # This shouldn't happen, but if it does, return a helpful error
            return HttpResponseBadRequest(
                "This development server only supports HTTP. "
                "Please use http://127.0.0.1:8000 or http://localhost:8000"
            )
        return self.get_response(request)

