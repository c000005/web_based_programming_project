# web_based_programming_project/weather_platform/controllers/auth_controller.py
import sqlite3
from core import auth, cookie, response
import settings
from .base_controller import render_template, render_error_page, parse_form_data


def handle_login_get():
    """Show login form"""
    html = render_template("login.html", {"title": "ورود به سیستم"})
    if html:
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    return render_error_page(500, "Template login.html not found")


def handle_login_post(body):
    """Handle user login"""
    form_data = parse_form_data(body)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '').strip()

    if not username or not password:
        return render_error_page(400, "نام کاربری و رمز عبور الزامی هستند")

    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT id, username, email, full_name, role, is_active
                   FROM users
                   WHERE username = ?
                   AND password_hash = ?
                   ''', (username, password))

    user = cursor.fetchone()
    conn.close()

    if not user:
        html = render_template("login.html", {
            "title": "ورود به سیستم",
            "error": "نام کاربری یا رمز عبور اشتباه است."
        })
        return html, 401, {"Content-Type": "text/html; charset=utf-8"}

    if not user['is_active']:
        html = render_template("login.html", {
            "title": "ورود به سیستم",
            "error": "حساب کاربری شما غیرفعال است. با پشتیبانی تماس بگیرید."
        })
        return html, 403, {"Content-Type": "text/html; charset=utf-8"}

    # Create session
    session_id = auth.create_session(user['id'])
    headers = cookie.set_cookie('session_id', session_id, max_age=86400)  # 1 day

    # Redirect to dashboard
    return """
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl mb-4">
        ✅ ورود با موفقیت انجام شد. خوش آمدید {}!
        <br>
        <a href="/weather_platform/dashboard" class="text-green-800 underline">رفتن به داشبورد</a>
    </div>
    """.format(user['full_name'] or user['username']), 200, {**headers, "Content-Type": "text/html; charset=utf-8"}


def handle_logout(headers):
    """Handle user logout"""
    # Get session from cookie
    cookie_header = headers.get('Cookie', '')
    session_id = None
    for cookie_str in cookie_header.split(';'):
        cookie_str = cookie_str.strip()
        if cookie_str.startswith('session_id='):
            session_id = cookie_str.split('=', 1)[1]
            break

    if session_id:
        auth.delete_session(session_id)

    headers = cookie.clear_cookie('session_id')
    return """
    <div class="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded-xl mb-4">
        👋 شما با موفقیت خارج شدید.
        <br>
        <a href="/weather_platform/login" class="text-blue-800 underline">ورود مجدد</a>
    </div>
    """, 200, {**headers, "Content-Type": "text/html; charset=utf-8"}


def get_current_user_from_headers(headers):
    """Get current user from request headers"""
    cookie_header = headers.get('Cookie', '')
    session_id = None
    for cookie_str in cookie_header.split(';'):
        cookie_str = cookie_str.strip()
        if cookie_str.startswith('session_id='):
            session_id = cookie_str.split('=', 1)[1]
            break

    if not session_id:
        return None

    return auth.get_user_by_session(session_id)