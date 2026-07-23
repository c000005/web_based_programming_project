# web_based_programming_project/weather_platform/controllers/report_controller.py

from .base_controller import render_template, render_error_page, get_db_connection


def handle_reports_list(user_display=""):
    """Show reports list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT id, title, report_type, start_date, end_date,
                              region, is_public, view_count, created_at
                       FROM analysis_reports
                       ORDER BY created_at DESC
                       ''')
        reports = cursor.fetchall()
        conn.close()

        table_rows = ""
        for report in reports:
            table_rows += f"""
            <tr>
                <td>{report['id']}</td>
                <td><strong>{report['title']}</strong></td>
                <td>{report['report_type'] or '-'}</td>
                <td>{report['start_date'] or '-'}</td>
                <td>{report['end_date'] or '-'}</td>
                <td>{report['region'] or '-'}</td>
                <td><span class="badge badge-info">{'🌐 Public' if report['is_public'] else '🔒 Private'}</span></td>
                <td>{report['view_count']}</td>
                <td>{report['created_at']}</td>
            </tr>
            """

        html = render_template("reports_list.html", {
            "title": "گزارش‌های تحلیلی",
            "reports_rows": table_rows,
            "user_display": user_display
        })
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template reports_list.html not found")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت گزارش‌ها: {e}")