"""
Middleware para evitar cache de HTML en navegadores.
Permite ver cambios de templates con un simple F5.
"""


class NoCacheHTMLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        content_type = (response.get("Content-Type") or "").lower()
        is_html = "text/html" in content_type
        is_get_like = request.method in ("GET", "HEAD")

        if is_html and is_get_like:
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            response["Surrogate-Control"] = "no-store"

        return response

