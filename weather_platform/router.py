# web_based_programming_project/weather_platform/router.py

import json
import sqlite3
from pathlib import Path
import importlib.util
import urllib.parse
import re

# run db_setup just one time
_db_initialized = False


def render_template(filename, context=None):
    """Render template with include support and variable substitution"""
    base_dir = Path(__file__).resolve().parent
    template_path = base_dir / "templates" / filename

    if not template_path.exists():
        return None

    content = template_path.read_text(encoding="utf-8")

    # Process includes recursively (max 5 levels deep)
    for _ in range(5):
        include_pattern = r'{%\s*include\s+"([^"]+)"\s*%}'
        matches = re.findall(include_pattern, content)

        if not matches:
            break

        for include_file in matches:
            include_path = base_dir / "templates" / include_file
            if include_path.exists():
                include_content = include_path.read_text(encoding="utf-8")
                content = content.replace(f'{{% include "{include_file}" %}}', include_content)

    # Process variables {{ variable }}
    if context:
        for key, value in context.items():
            content = content.replace(f"{{{{ {key} }}}}", str(value))

    # Remove any unprocessed variables (like {{ extra_css }} if not provided)
    content = re.sub(r'{{\s*[^}]+?\s*}}', '', content)

    return content


def run_db_setup():
    """Initialize database if not exists"""
    base_dir = Path(__file__).resolve().parent
    db_setup_path = base_dir / "db_setup.py"

    if not db_setup_path.exists():
        return "db_setup.py not found"

    spec = importlib.util.spec_from_file_location("weather_platform_setup", db_setup_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "setup_database"):
        module.setup_database()
        return "Database setup completed"
    return "setup_database() not found in db_setup.py"


def get_db_connection():
    """Get database connection"""
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / "weather_platform.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def parse_form_data(body):
    """Parse application/x-www-form-urlencoded body"""
    if not body:
        return {}
    if isinstance(body, bytes):
        body = body.decode('utf-8')
    return dict(urllib.parse.parse_qsl(body))


def route(path, method, body):
    """Main routing function"""

    # GET request handling
    if method == "GET":

        # Setup route
        if path == "/setup":
            result = run_db_setup()
            return f"<p>{result}</p>", 200, {"Content-Type": "text/html; charset=utf-8"}

        # Home page
        elif path == "/":
            html = render_template("index.html", {"title": "پلتفرم هواشناسی"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template index.html not found", 500, {"Content-Type": "text/plain"}

        # Contact page
        elif path == "/contact":
            html = render_template("contact.html", {"title": "تماس با ما"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template contact.html not found", 500, {"Content-Type": "text/plain"}

        # Register page
        elif path == "/register":
            html = render_template("register.html", {"title": "ثبت‌نام"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template register.html not found", 500, {"Content-Type": "text/plain"}

        # Add weather form
        elif path == "/add_weather":
            html = render_template("add_weather.html", {"title": "ثبت داده هواشناسی"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template add_weather.html not found", 500, {"Content-Type": "text/plain"}

        # About page
        elif path == "/about":
            html = render_template("about.html", {"title": "درباره ما"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template about.html not found", 500, {"Content-Type": "text/plain"}

        # New message form
        elif path == "/messages/new":
            html = render_template("message_form.html", {"title": "ارسال پیام جدید"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template message_form.html not found", 500, {"Content-Type": "text/plain"}

        # New user form
        elif path == "/users/new":
            html = render_template("user_form.html", {"title": "ثبت نام کاربر جدید"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template user_form.html not found", 500, {"Content-Type": "text/plain"}

        # New product form
        elif path == "/products/new":
            html = render_template("product_form.html", {"title": "افزودن محصول جدید"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template product_form.html not found", 500, {"Content-Type": "text/plain"}

        # Users list
        elif path == "/admin/users":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, username, email, full_name, role, is_active, created_at FROM users ORDER BY created_at DESC')
                users = cursor.fetchall()
                conn.close()

                table_rows = ""
                for user in users:
                    status_class = "badge-success" if user['is_active'] else "badge-danger"
                    status_text = "✅ Active" if user['is_active'] else "❌ Inactive"
                    table_rows += f"""
                    <tr>
                        <td>{user['id']}</td>
                        <td><strong>{user['username']}</strong></td>
                        <td>{user['email']}</td>
                        <td>{user['full_name'] or '-'}</td>
                        <td><span class="badge badge-primary">{user['role']}</span></td>
                        <td><span class="badge {status_class}">{status_text}</span></td>
                        <td>{user['created_at']}</td>
                    </tr>
                    """

                html = render_template("users_list.html", {"title": "لیست کاربران", "users_rows": table_rows})
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return "Template users_list.html not found", 500, {"Content-Type": "text/plain"}
            except Exception as e:
                return f"<p style='color:red'>Error fetching users: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # Weather list
        elif path == "/weather/list":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               SELECT id,
                                      station_code,
                                      city_name,
                                      country,
                                      record_date,
                                      temperature_celsius,
                                      humidity_percent,
                                      pressure_hpa,
                                      wind_speed_ms,
                                      weather_condition
                               FROM weather_data
                               ORDER BY record_date DESC LIMIT 50
                               ''')
                weather_data = cursor.fetchall()
                conn.close()

                table_rows = ""
                for wd in weather_data:
                    table_rows += f"""
                    <tr>
                        <td>{wd['id']}</td>
                        <td>{wd['station_code']}</td>
                        <td>{wd['city_name']}</td>
                        <td>{wd['country']}</td>
                        <td>{wd['record_date']}</td>
                        <td>{wd['temperature_celsius'] if wd['temperature_celsius'] else '-'}</td>
                        <td>{wd['humidity_percent'] if wd['humidity_percent'] else '-'}</td>
                        <td>{wd['pressure_hpa'] if wd['pressure_hpa'] else '-'}</td>
                        <td>{wd['wind_speed_ms'] if wd['wind_speed_ms'] else '-'}</td>
                        <td>{wd['weather_condition'] or '-'}</td>
                    </tr>
                    """

                html = render_template("weather_list.html", {"title": "داده‌های هواشناسی", "weather_rows": table_rows})
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return "Template weather_list.html not found", 500, {"Content-Type": "text/plain"}
            except Exception as e:
                return f"<p style='color:red'>Error fetching weather data: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # Messages list
        elif path == "/admin/messages":
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
                    </tr>
                    """

                html = render_template("messages_list.html", {"title": "لیست پیام‌ها", "messages_rows": table_rows})
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return "Template messages_list.html not found", 500, {"Content-Type": "text/plain"}
            except Exception as e:
                return f"<p style='color:red'>Error fetching messages: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # Products list
        elif path == "/products/list":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, name, description, price, category, is_active, created_at FROM products ORDER BY created_at DESC')
                products = cursor.fetchall()
                conn.close()

                table_rows = ""
                for product in products:
                    status_class = "badge-success" if product['is_active'] else "badge-danger"
                    status_text = "✅ Active" if product['is_active'] else "❌ Inactive"
                    price_display = f"{product['price']:,.0f}" if product['price'] else "-"
                    table_rows += f"""
                    <tr>
                        <td>{product['id']}</td>
                        <td><strong>{product['name']}</strong></td>
                        <td>{product['description'] or '-'}</td>
                        <td><strong>{price_display}</strong></td>
                        <td><span class="badge badge-info">{product['category'] or '-'}</span></td>
                        <td><span class="badge {status_class}">{status_text}</span></td>
                        <td>{product['created_at']}</td>
                    </tr>
                    """

                html = render_template("products_list.html", {"title": "لیست محصولات", "products_rows": table_rows})
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return "Template products_list.html not found", 500, {"Content-Type": "text/plain"}
            except Exception as e:
                return f"<p style='color:red'>Error fetching products: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # Products catalog
        elif path == "/products/catalog":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               SELECT id, name, description, price, category, is_active, created_at
                               FROM products
                               WHERE is_active = 1
                               ORDER BY created_at DESC
                               ''')
                products = cursor.fetchall()
                conn.close()

                catalog_cards = ""
                for product in products:
                    category_icon = "📦"
                    category_name = product['category'] or 'Other'
                    if product['category'] == 'subscription':
                        category_icon = "📅"
                        category_name = "اشتراک"
                    elif product['category'] == 'api_access':
                        category_icon = "🔌"
                        category_name = "دسترسی API"
                    elif product['category'] == 'custom_report':
                        category_icon = "📊"
                        category_name = "گزارش سفارشی"

                    price_display = f"{product['price']:,.0f}" if product['price'] else "تماس بگیرید"
                    catalog_cards += f'''
                    <div class="product-card" data-title="{product['name']}" data-description="{product['description'] or ''}" data-category="{product['category'] or 'other'}">
                        <div class="product-image">
                            <span>{category_icon}</span>
                        </div>
                        <div class="product-body">
                            <h3>{product['name']}</h3>
                            <span class="category">{category_icon} {category_name}</span>
                            <p class="description">{product['description'] or 'توضیحاتی برای این محصول ثبت نشده است'}</p>
                            <div class="price">{price_display}</div>
                            <div class="actions">
                                <a href="#" class="btn btn-primary">خرید</a>
                                <a href="#" class="btn btn-secondary">اطلاعات بیشتر</a>
                            </div>
                        </div>
                    </div>
                    '''

                html = render_template("catalog.html", {"title": "کاتالوگ محصولات", "catalog_cards": catalog_cards})
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return "Template catalog.html not found", 500, {"Content-Type": "text/plain"}
            except Exception as e:
                return f"<p style='color:red'>Error fetching catalog: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # Dashboard
        elif path == "/dashboard":
            html = render_template("dashboard.html", {"title": "داشبورد مدیریت"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template dashboard.html not found", 500, {"Content-Type": "text/plain"}

        # Reports list
        elif path == "/reports/list":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               SELECT id,
                                      title,
                                      report_type,
                                      start_date,
                                      end_date,
                                      region,
                                      is_public,
                                      view_count,
                                      created_at
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

                html = render_template("reports_list.html", {"title": "گزارش‌های تحلیلی", "reports_rows": table_rows})
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return "Template reports_list.html not found", 500, {"Content-Type": "text/plain"}
            except Exception as e:
                return f"<p style='color:red'>Error fetching reports: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # API status
        elif path == "/api/status":
            data = {"project": "weather_platform", "status": "ok"}
            return json.dumps(data, ensure_ascii=False), 200, {"Content-Type": "application/json"}

        # 404
        else:
            html = render_template("404.html", {"title": "صفحه یافت نشد"})
            if html:
                return html, 404, {"Content-Type": "text/html; charset=utf-8"}
            return "Not Found", 404, {"Content-Type": "text/plain; charset=utf-8"}

    # POST request handling
    elif method == "POST":
        form_data = parse_form_data(body)

        # Handle message form submission
        if path == "/messages/new":
            name = form_data.get('name', '').strip()
            email = form_data.get('email', '').strip()
            subject = form_data.get('subject', '').strip()
            message = form_data.get('message', '').strip()

            if not name or not email or not message:
                return """<p style='color:red'>Error: name, email and message are required.</p>""", 400, {
                    "Content-Type": "text/html; charset=utf-8"}

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               INSERT INTO messages (name, email, subject, message)
                               VALUES (?, ?, ?, ?)
                               ''', (name, email, subject, message))
                conn.commit()
                conn.close()
                return """<p style='color:green'>✅ Message saved successfully.</p>""", 200, {
                    "Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return f"<p style='color:red'>Error saving message: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # Handle user registration
        elif path == "/register":
            username = form_data.get('username', '').strip()
            password_hash = form_data.get('password', '').strip()
            email = form_data.get('email', '').strip()
            full_name = form_data.get('full_name', '').strip()
            role = form_data.get('role', 'viewer')

            if not username or not password_hash or not email:
                return "<p style='color:red'>Error: username, password and email are required.</p>", 400, {
                    "Content-Type": "text/html; charset=utf-8"}

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
                return f"<p style='color:red'>Error: username or email already exists. ({e})</p>", 400, {
                    "Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return f"<p style='color:red'>Error registering user: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # Handle product addition
        elif path == "/products/new":
            name = form_data.get('name', '').strip()
            description = form_data.get('description', '').strip()
            price = form_data.get('price', '')
            category = form_data.get('category', '')
            is_active = form_data.get('is_active', '1')

            if not name:
                return "<p style='color:red'>Error: product name is required.</p>", 400, {
                    "Content-Type": "text/html; charset=utf-8"}

            try:
                price_float = float(price) if price else None
            except ValueError:
                price_float = None

            is_active_int = 1 if is_active == '1' else 0

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               INSERT INTO products (name, description, price, category, is_active)
                               VALUES (?, ?, ?, ?, ?)
                               ''', (name, description, price_float, category, is_active_int))
                conn.commit()
                conn.close()
                return "<p style='color:green'>✅ New product added successfully!</p>", 200, {
                    "Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return f"<p style='color:red'>Error adding product: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # Handle weather data addition
        elif path == "/add_weather":
            station_code = form_data.get('station_code', '').strip()
            city_name = form_data.get('city_name', '').strip()
            country = form_data.get('country', '').strip()
            record_date = form_data.get('record_date', '')
            temperature = form_data.get('temperature', '')
            humidity = form_data.get('humidity', '')
            pressure = form_data.get('pressure', '')
            wind_speed = form_data.get('wind_speed', '')
            weather_condition = form_data.get('weather_condition', '').strip()

            if not station_code or not city_name or not country or not record_date:
                return "<p style='color:red'>Error: station_code, city_name, country and record_date are required.</p>", 400, {
                    "Content-Type": "text/html; charset=utf-8"}

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               INSERT INTO weather_data (station_code, city_name, country, record_date,
                                                         temperature_celsius, humidity_percent, pressure_hpa,
                                                         wind_speed_ms, weather_condition)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                               ''', (station_code, city_name, country, record_date,
                                     float(temperature) if temperature else None,
                                     float(humidity) if humidity else None,
                                     float(pressure) if pressure else None,
                                     float(wind_speed) if wind_speed else None,
                                     weather_condition))
                conn.commit()
                conn.close()
                return "<p style='color:green'>✅ Weather data saved successfully!</p>", 200, {
                    "Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return f"<p style='color:red'>Error saving weather data: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

    # Method not allowed
    return "Method not allowed", 405, {"Content-Type": "text/plain; charset=utf-8"}