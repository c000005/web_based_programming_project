# web_based_programming_project/weather_platform/controllers/base_controller.py

import json
import sqlite3
from pathlib import Path
import re
import html

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"


def get_db_connection():
    """Get database connection"""
    db_path = BASE_DIR / "weather_platform.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def render_template(filename, context=None):
    """
    Render template with support for:
    - {% include "file.html" %} - include other templates
    - {{ variable }} - variable substitution
    - {% if condition %} ... {% endif %} - simple conditionals
    - {% for item in items %} ... {% endfor %} - simple loops
    """
    template_path = TEMPLATE_DIR / filename

    if not template_path.exists():
        return None

    content = template_path.read_text(encoding="utf-8")

    # Process includes recursively
    for _ in range(5):
        include_pattern = r'{%\s*include\s+"([^"]+)"\s*%}'
        matches = re.findall(include_pattern, content)

        if not matches:
            break

        for include_file in matches:
            include_path = TEMPLATE_DIR / include_file
            if include_path.exists():
                include_content = include_path.read_text(encoding="utf-8")
                content = content.replace(f'{{% include "{include_file}" %}}', include_content)

    # Process {% if condition %} ... {% endif %}
    if context:
        # Process if statements
        if_pattern = r'{%\s*if\s+([^%]+)%}(.*?){%\s*endif\s*%}'
        matches = re.findall(if_pattern, content, re.DOTALL)

        for condition, block in matches:
            condition = condition.strip()
            # Evaluate condition
            if condition in context:
                value = context[condition]
                if value:
                    content = content.replace(f'{{% if {condition} %}}{block}{{% endif %}}', block)
                else:
                    content = content.replace(f'{{% if {condition} %}}{block}{{% endif %}}', '')
            else:
                # If condition variable doesn't exist, remove the block
                content = content.replace(f'{{% if {condition} %}}{block}{{% endif %}}', '')

        # Process for loops: {% for item in items %} ... {% endfor %}
        for_pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
        matches = re.findall(for_pattern, content, re.DOTALL)

        for item_var, list_var, block in matches:
            if list_var in context and isinstance(context[list_var], (list, tuple)):
                items = context[list_var]
                result = ""
                for item in items:
                    # Create a context with the item
                    item_context = context.copy()
                    if isinstance(item, dict):
                        # If item is a dict, merge its keys into context
                        item_context.update(item)
                    item_context[item_var] = item

                    # Process the block with the item context
                    block_content = block
                    for key, value in item_context.items():
                        if isinstance(value, (str, int, float, bool)):
                            block_content = block_content.replace(f"{{{{ {key} }}}}", str(value))
                    result += block_content
                content = content.replace(f'{{% for {item_var} in {list_var} %}}{block}{{% endfor %}}', result)
            else:
                # If list doesn't exist, remove the block
                content = content.replace(f'{{% for {item_var} in {list_var} %}}{block}{{% endfor %}}', '')

        # Process simple variables {{ variable }}
        for key, value in context.items():
            # Don't replace complex objects, only strings and basic types
            if isinstance(value, (str, int, float, bool)):
                content = content.replace(f"{{{{ {key} }}}}", str(value))
            elif value is None:
                content = content.replace(f"{{{{ {key} }}}}", '')

    # Remove any unprocessed template tags (cleanup)
    content = re.sub(r'{%\s*[^%]+?\s*%}', '', content)
    content = re.sub(r'{{\s*[^}]+?\s*}}', '', content)

    return content


def render_error_page(status_code, message=""):
    """Render error pages for 400, 403, 404, 405, 500"""
    status_messages = {
        400: "Bad Request",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error"
    }

    error_icons = {
        400: "❌",
        403: "⛔",
        404: "🔍",
        405: "🚫",
        500: "💥"
    }

    error_titles = {
        400: "درخواست نامعتبر",
        403: "دسترسی ممنوع",
        404: "صفحه یافت نشد",
        405: "روش غیرمجاز",
        500: "خطای سرور"
    }

    icon = error_icons.get(status_code, "⚠️")
    title = error_titles.get(status_code, "خطا")
    status_text = status_messages.get(status_code, "Error")

    html = render_template("error.html", {
        "title": title,
        "status_code": status_code,
        "status_text": status_text,
        "icon": icon,
        "message": message,
        "error_type": f"error-{status_code}"
    })

    if html:
        return html, status_code, {"Content-Type": "text/html; charset=utf-8"}

    # Fallback if template not found
    fallback_html = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: 'Vazir', 'IRANSans', 'Tahoma', sans-serif;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                direction: rtl;
            }}
            .error-container {{
                background: white;
                border-radius: 20px;
                padding: 50px;
                text-align: center;
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
                max-width: 500px;
                width: 100%;
            }}
            .error-icon {{
                font-size: 80px;
                margin-bottom: 20px;
            }}
            .error-title {{
                font-size: 28px;
                color: #333;
                margin-bottom: 10px;
            }}
            .error-code {{
                font-size: 72px;
                font-weight: bold;
                color: #e74c3c;
                margin: 10px 0;
            }}
            .error-message {{
                color: #666;
                margin: 20px 0;
                font-size: 16px;
            }}
            .btn-home {{
                display: inline-block;
                padding: 12px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                transition: all 0.3s;
                margin-top: 10px;
            }}
            .btn-home:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(0,0,0,0.2);
            }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <div class="error-icon">{icon}</div>
            <div class="error-code">{status_code}</div>
            <h1 class="error-title">{title}</h1>
            {f'<p class="error-message">{message}</p>' if message else ''}
            <a href="/weather_platform/dashboard" class="btn-home">🏠 بازگشت به داشبورد</a>
        </div>
    </body>
    </html>
    """
    return fallback_html, status_code, {"Content-Type": "text/html; charset=utf-8"}


def parse_form_data(body):
    """
    Parse application/x-www-form-urlencoded body
    Handles both bytes and string input
    """
    import urllib.parse

    if not body:
        return {}

    # If body is already a dict, return it
    if isinstance(body, dict):
        return body

    # If body is bytes, decode and parse
    if isinstance(body, bytes):
        try:
            body_str = body.decode('utf-8')
        except UnicodeDecodeError:
            return {}
    elif isinstance(body, str):
        body_str = body
    else:
        return {}

    # Parse the query string
    return dict(urllib.parse.parse_qsl(body_str))


def json_response(data, status=200):
    """Return JSON response"""
    return json.dumps(data, ensure_ascii=False), status, {"Content-Type": "application/json"}