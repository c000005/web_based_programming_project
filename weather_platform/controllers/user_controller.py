# web_based_programming_project/weather_platform/controllers/user_controller.py

from .base_controller import render_template, render_error_page, get_db_connection, parse_form_data


def handle_user_form(headers=None):
    """Show new user form"""
    html = render_template("register.html", {"title": "ثبت نام کاربر جدید"})
    if html:
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    return render_error_page(500, "Template register.html not found")


def handle_user_edit_get(path, headers=None):
    """Show edit user form"""
    try:
        user_id = int(path.split("/")[-1])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, email, full_name, role, is_active FROM users WHERE id = ?',
            (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return render_error_page(404, f"کاربر با شناسه {user_id} یافت نشد")

        html = render_template("user_edit.html", {
            "title": "ویرایش کاربر",
            "user_id": user_id,
            "username": user['username'],
            "email": user['email'],
            "full_name": user['full_name'] or '',
            "role": user['role'],
            "is_active_checked": "checked" if user['is_active'] else ""
        })
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template user_edit.html not found")
    except ValueError:
        return render_error_page(404, "شناسه نامعتبر")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت کاربر: {e}")


def handle_user_edit_post(path, body, headers=None):
    """Process user edit"""
    try:
        user_id = int(path.split("/")[-1])
        form_data = parse_form_data(body)
        username = form_data.get('username', '').strip()
        email = form_data.get('email', '').strip()
        full_name = form_data.get('full_name', '').strip()
        role = form_data.get('role', 'viewer')
        is_active = form_data.get('is_active', '0')

        if not username or not email:
            return render_error_page(400, "نام کاربری و ایمیل الزامی هستند")

        is_active_int = 1 if is_active == '1' else 0

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       UPDATE users
                       SET username = ?, email = ?, full_name = ?, role = ?, is_active = ?
                       WHERE id = ?
                       ''', (username, email, full_name, role, is_active_int, user_id))

        if cursor.rowcount == 0:
            conn.close()
            return render_error_page(404, f"کاربر با شناسه {user_id} یافت نشد")

        conn.commit()
        conn.close()
        return '<p style="color:green">✅ User updated successfully!</p>', 200, {
            "Content-Type": "text/html; charset=utf-8"}
    except ValueError:
        return render_error_page(400, "شناسه نامعتبر")
    except Exception as e:
        return render_error_page(500, f"خطا در بروزرسانی کاربر: {e}")


def handle_users_list(headers=None):
    """Show users list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, email, full_name, role, is_active, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()

        # Convert to list of dicts for template
        users_list = []
        for user in users:
            users_list.append({
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name'] or '-',
                'role': user['role'],
                'is_active': user['is_active'],
                'created_at': user['created_at']
            })

        html = render_template("users_list.html", {
            "title": "لیست کاربران",
            "users": users_list
        })
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template users_list.html not found")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت کاربران: {e}")