# web_based_programming_project/weather_platform/controllers/auth_controller.py

from .base_controller import render_template, render_error_page, get_db_connection, parse_form_data
import sqlite3


def handle_register_get():
    """Show registration page"""
    html = render_template("register.html", {"title": "ثبت‌نام"})
    if html:
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    return render_error_page(500, "Template register.html not found")


def handle_register_post(body):
    """Process registration form"""
    form_data = parse_form_data(body)
    username = form_data.get('username', '').strip()
    password_hash = form_data.get('password', '').strip()
    email = form_data.get('email', '').strip()
    full_name = form_data.get('full_name', '').strip()
    role = form_data.get('role', 'viewer')

    if not username or not password_hash or not email:
        return render_error_page(400, "نام کاربری، رمز عبور و ایمیل الزامی هستند")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO users (username, password_hash, email, full_name, role, is_active)
                       VALUES (?, ?, ?, ?, ?, 1)
                       ''', (username, password_hash, email, full_name, role))
        conn.commit()
        conn.close()
        return "<p style='color:green'>✅ Registration successful!</p>", 200, {
            "Content-Type": "text/html; charset=utf-8"}
    except sqlite3.IntegrityError as e:
        return render_error_page(400, f"نام کاربری یا ایمیل تکراری است. ({e})")
    except Exception as e:
        return render_error_page(500, f"خطا در ثبت نام: {e}")