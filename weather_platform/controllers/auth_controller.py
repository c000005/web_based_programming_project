# web_based_programming_project/weather_platform/controllers/auth_controller.py
import sqlite3
from core import auth, cookie, response
import settings
from .base_controller import render_template, render_error_page, parse_form_data


def handle_login_get():
    """Show login form"""
    html = render_template("login.html", {"title": "ورود به سیستم", "error": None})
    if html:
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    return render_error_page(500, "Template login.html not found")


def handle_login_post(body):
    """Handle user login"""
    # body could be bytes or dict depending on how it's passed
    if isinstance(body, dict):
        form_data = body
    else:
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
        error_html = '''
        <div class="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 m-6 rounded-lg">
            <p class="font-bold">⚠️ خطا</p>
            <p>نام کاربری یا رمز عبور اشتباه است. لطفاً دوباره تلاش کنید.</p>
        </div>
        '''
        html = render_template("login.html", {
            "title": "ورود به سیستم",
            "error_html": error_html
        })
        return html, 401, {"Content-Type": "text/html; charset=utf-8"}

    # Create session
    session_id = auth.create_session(user['id'])
    headers = cookie.set_cookie('session_id', session_id, max_age=86400)

    # Return success with redirect
    return """
    <div style="max-width: 500px; margin: 50px auto; background: white; padding: 40px; border-radius: 15px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
        <div style="color: #155724; background-color: #d4edda; border-color: #c3e6cb; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h2>✅ ورود موفق!</h2>
            <p>خوش آمدید {}</p>
        </div>
        <a href="/weather_platform/dashboard" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 10px;">رفتن به داشبورد</a>
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
    <div style="max-width: 500px; margin: 50px auto; background: white; padding: 40px; border-radius: 15px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
        <div style="color: #0c5460; background-color: #d1ecf1; border-color: #bee5eb; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h2>👋 خروج موفق</h2>
            <p>شما با موفقیت خارج شدید.</p>
        </div>
        <a href="/weather_platform/login" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 10px;">ورود مجدد</a>
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


def handle_register_post(body):
    """Handle user registration"""
    # body could be bytes or dict depending on how it's passed
    if isinstance(body, dict):
        form_data = body
    else:
        form_data = parse_form_data(body)

    username = form_data.get('username', '').strip()
    email = form_data.get('email', '').strip()
    password = form_data.get('password', '').strip()
    role = form_data.get('role', 'viewer')

    if not username or not email or not password:
        return render_error_page(400, "همه فیلدها الزامی هستند")

    try:
        conn = sqlite3.connect(settings.DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO users (username, email, password_hash, role)
                       VALUES (?, ?, ?, ?)
                       ''', (username, email, password, role))
        conn.commit()
        conn.close()

        return """
        <div style="max-width: 500px; margin: 50px auto; background: white; padding: 40px; border-radius: 15px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
            <div style="color: #155724; background-color: #d4edda; border-color: #c3e6cb; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h2>✅ ثبت‌نام موفق!</h2>
                <p>کاربر {} با موفقیت ثبت شد.</p>
            </div>
            <a href="/weather_platform/login" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 10px;">ورود به سیستم</a>
        </div>
        """.format(username), 200, {"Content-Type": "text/html; charset=utf-8"}
    except sqlite3.IntegrityError:
        return render_error_page(400, "نام کاربری یا ایمیل قبلاً ثبت شده است")
    except Exception as e:
        return render_error_page(500, f"خطا در ثبت‌نام: {e}")