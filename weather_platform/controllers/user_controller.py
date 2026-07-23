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

        # Get user_display from headers
        from .auth_controller import get_user_display_from_headers
        user_display = get_user_display_from_headers(headers) if headers else ""

        html = render_template("user_edit.html", {
            "title": "ویرایش کاربر",
            "user_id": user_id,
            "username": user['username'],
            "email": user['email'],
            "full_name": user['full_name'] or '',
            "role": user['role'],
            "is_active_checked": "checked" if user['is_active'] else "",
            "user_display": user_display
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
                       SET username  = ?,
                           email     = ?,
                           full_name = ?,
                           role      = ?,
                           is_active = ?
                       WHERE id = ?
                       ''', (username, email, full_name, role, is_active_int, user_id))

        if cursor.rowcount == 0:
            conn.close()
            return render_error_page(404, f"کاربر با شناسه {user_id} یافت نشد")

        conn.commit()
        conn.close()

        # Redirect back to users list with success message
        return """
        <div style="max-width: 600px; margin: 50px auto; background: white; padding: 30px; border-radius: 15px; text-align: center; box-shadow: 0 10px 40px rgba(0,0,0,0.2);">
            <div style="color: #155724; background-color: #d4edda; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
                <h2>✅ کاربر با موفقیت بروزرسانی شد!</h2>
            </div>
            <a href="/weather_platform/admin/users" class="btn btn-primary" style="display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 10px;">بازگشت به لیست کاربران</a>
        </div>
        """, 200, {"Content-Type": "text/html; charset=utf-8"}
    except ValueError:
        return render_error_page(400, "شناسه نامعتبر")
    except Exception as e:
        return render_error_page(500, f"خطا در بروزرسانی کاربر: {e}")


def handle_users_list(headers=None, user_display=""):
    """Show users list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, username, email, full_name, role, is_active, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()

        # Build HTML rows in the controller
        table_rows = ""
        for user in users:
            status_class = "badge-success" if user['is_active'] else "badge-danger"
            status_text = "✅ Active" if user['is_active'] else "❌ Inactive"
            full_name = user['full_name'] or '-'

            table_rows += f"""
            <tr>
                <td>{user['id']}</td>
                <td><strong>{user['username']}</strong></td>
                <td>{user['email']}</td>
                <td>{full_name}</td>
                <td><span class="badge badge-primary">{user['role']}</span></td>
                <td><span class="badge {status_class}">{status_text}</span></td>
                <td>{user['created_at']}</td>
                <td>
                    <a href="/weather_platform/admin/users/edit/{user['id']}" class="btn btn-sm btn-primary">✏️ ویرایش</a>
                </td>
            </tr>
            """

        html = render_template("users_list.html", {
            "title": "لیست کاربران",
            "users_rows": table_rows,
            "user_display": user_display
        })
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template users_list.html not found")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت کاربران: {e}")