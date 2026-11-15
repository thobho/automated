import logging

from . import services

logger = logging.getLogger(__name__)


class VisitMiddleware:
    """Counts successful HTML GET page views. Sets no cookie and never breaks a request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method == "GET"
            and response.status_code == 200
            and response.get("Content-Type", "").startswith("text/html")
        ):
            try:
                services.record_visit(
                    request.path,
                    request.META.get("REMOTE_ADDR", ""),
                    request.META.get("HTTP_USER_AGENT", ""),
                )
            except Exception:  # analytics must never take a page down
                logger.exception("visit_record_failed")
        return response
