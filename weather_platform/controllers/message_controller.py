# web_based_programming_project/weather_platform/controllers/message_controller.py

from .base_controller import render_template, render_error_page, get_db_connection, parse_form_data


def handle_message_form(headers=None):
    """Show new message form"""
    html = render_template("message_form.html", {"title": "ارسال پیام جدید"})
    if html:
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    return render_error_page(500, "Template message_form.html not found")


def handle_message_new_post(body, headers=None):
    """Process message submission"""
    form_data = parse_form_data(body)
    name = form_data.get('name', '').strip()
    email = form_data.get('email', '').strip()
    subject = form_data.get('subject', '').strip()
    message = form_data.get('message', '').strip()

    if not name or not email or not message:
        return render_error_page(400, "نام، ایمیل و پیام الزامی هستند")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO messages (name, email, subject, message)
                       VALUES (?, ?, ?, ?)
                       ''', (name, email, subject, message))
        conn.commit()
        conn.close()
        return '<p style="color:green">✅ Message saved successfully!</p>', 200, {
            "Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return render_error_page(500, f"خطا در ذخیره پیام: {e}")


def handle_message_view(path, headers=None):
    """View single message"""
    try:
        message_id = int(path.split("/")[-1])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, email, subject, message, is_read, created_at FROM messages WHERE id = ?',
            (message_id,))
        message = cursor.fetchone()
        conn.close()

        if not message:
            return render_error_page(404, f"پیام با شناسه {message_id} یافت نشد")

        html = render_template("message_view.html", {
            "title": "نمایش پیام",
            "message_id": message_id,
            "name": message['name'],
            "email": message['email'],
            "subject": message['subject'] or 'بدون موضوع',
            "message": message['message'],
            "is_read": message['is_read'],
            "is_read_text": "خوانده شده" if message['is_read'] else "خوانده نشده",
            "created_at": message['created_at']
        })
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template message_view.html not found")
    except ValueError:
        return render_error_page(404, "شناسه نامعتبر")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت پیام: {e}")


def handle_messages_list(headers=None):
    """Show messages list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, email, subject, message, is_read, created_at FROM messages ORDER BY created_at DESC')
        messages = cursor.fetchall()
        conn.close()

        table_rows = ""
        for msg in messages:
            status_class = "badge-success" if msg['is_read'] else "badge-warning"
            status_text = "✅ Read" if msg['is_read'] else "📩 Unread"
            short_message = msg['message'][:50] + "..." if len(msg['message']) > 50 else msg['message']
            table_rows += f"""
            <tr>
                <td>{msg['id']}</td>
                <td><strong>{msg['name']}</strong></td>
                <td>{msg['email']}</td>
                <td>{msg['subject'] or '-'}</td>
                <td>{short_message}</td>
                <td><span class="badge {status_class}">{status_text}</span></td>
                <td>{msg['created_at']}</td>
                <td>
                    <a href="/weather_platform/messages/view/{msg['id']}" class="btn btn-sm btn-info">👁️ مشاهده</a>
                </td>
            </tr>
            """

        html = render_template("messages_list.html", {"title": "لیست پیام‌ها", "messages_rows": table_rows})
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template messages_list.html not found")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت پیام‌ها: {e}")