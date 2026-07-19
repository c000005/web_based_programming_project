# web_based_programming_project/weather_platform/core/response.py
import mimetypes
from pathlib import Path
import settings


def render_template(filename, context=None):
    """Render HTML template with variable substitution"""
    template_path = settings.TEMPLATE_DIR / filename

    if not template_path.exists():
        return None

    html = template_path.read_text(encoding="utf-8")

    # Replace variables {{ key }}
    if context:
        for key, value in context.items():
            html = html.replace(f"{{{{ {key} }}}}", str(value))

    return html


def serve_html(html, headers=None):
    """Serve HTML response"""
    if html:
        return _200(html, headers)
    return _500()


def serve_static_file(path):
    """Serve static files (CSS, JS, images)"""
    # Remove /static/ prefix if present
    if path.startswith("/static/"):
        path = path[8:]

    file_path = settings.STATIC_DIR / path

    if not file_path.exists():
        return _404()

    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = "application/octet-stream"

    body = file_path.read_bytes()
    return (body, 200, {"Content-Type": content_type})


def _200(html, headers=None):
    """200 OK response"""
    response_headers = {"Content-Type": "text/html; charset=utf-8"}
    if headers:
        response_headers.update(headers)
    return (html, 200, response_headers)


def _404():
    """404 Not Found response"""
    html = render_template("404.html", {
        "title": "صفحه یافت نشد",
        "message": "صفحه یا منبع مورد نظر پیدا نشد."
    })
    if html:
        return (html, 404, {"Content-Type": "text/html; charset=utf-8"})
    return ("صفحه یا منبع مورد نظر پیدا نشد.", 404, {"Content-Type": "text/plain; charset=utf-8"})


def _500():
    """500 Internal Server Error response"""
    return ("خطای داخلی سرور", 500, {"Content-Type": "text/plain; charset=utf-8"})


def _403():
    """403 Forbidden response"""
    html = render_template("403.html", {
        "title": "دسترسی ممنوع",
        "message": "شما دسترسی لازم برای مشاهده این صفحه را ندارید."
    })
    if html:
        return (html, 403, {"Content-Type": "text/html; charset=utf-8"})
    return ("دسترسی ممنوع", 403, {"Content-Type": "text/plain; charset=utf-8"})