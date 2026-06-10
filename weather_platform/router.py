# web_based_programming_project/weather_platform/router.py

import json
import sqlite3
from pathlib import Path
import importlib.util
import urllib.parse
from unittest import case

# run db_setup just one time

_db_initialized = False

def run_db_setup():

    # system route for file

    base_dir = Path(__file__).resolve().parent

    db_setup_path = base_dir / "db_setup.py"

    if not db_setup_path.exists():

        return "db_setup.py not found"

    # import module

    spec = importlib.util.spec_from_file_location("weather_platform_setup", db_setup_path)

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    # run the main method

    if hasattr(module, "setup_database"):

        module.setup_database()

        return "Database setup completed"

    return "setup_database() not found in db_setup.py"

# helper function to load file content

def render_template(filename):

    base_dir = Path(__file__).resolve().parent

    template_path = base_dir / "templates" / filename

    if not template_path.exists():

        return None

    return template_path.read_text(encoding="utf-8")

# helper function to get database connection
def get_db_connection():
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / "weather_platform.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # to access columns by name
    return conn

# helper function to parse POST body (form data)
def parse_form_data(body):
    """Parse application/x-www-form-urlencoded body"""
    if not body:
        return {}
    # body is bytes, decode to string
    if isinstance(body, bytes):
        body = body.decode('utf-8')
        return dict(urllib.parse.parse_qsl(body))

# main routing function

def route(path, method, body):

    # main page (index.html)

    match path:

        case "/setup":

            result = run_db_setup()

            return f"<p>{result}</p>", 200, {"Content-Type": "text/html; charset=utf-8"}

        case "/":

            html = render_template("index.html")

            if html:

                return html, 200, {"Content-Type": "text/html; charset=utf-8"}

            return "Template index.html not found", 500, {"Content-Type": "text/plain"}

        # contact route

        case "/contact":

            html = render_template("contact.html")

            if html:

                return html, 200, {"Content-Type": "text/html; charset=utf-8"}

            return "Template contact.html not found", 500, {"Content-Type": "text/plain"}

        # register route

        case "/register":
            html = render_template("register.html")

            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}

            return "Template register.html not found", 500, {"Content-Type": "text/plain"}

        # add_weather route

        case "/add_weather":
            html = render_template("add_weather.html")

            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}

            return "Template add_weather.html not found", 500, {"Content-Type": "text/plain"}

        # about route
        case "/about":

            html = render_template("about.html")

            if html:

                return html, 200, {"Content-Type": "text/html; charset=utf-8"}

            return "Template about.html not found", 500, {"Content-Type": "text/plain"}

        # add new message (messages table)
        case "/messages/new" if method == "GET":
            html = render_template("message_form.html")
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}

            return "Template message_form.html not found", 500, {"Content-Type": "text/plain"}

        case "/messages/new" if method == "POST":
            form_data = parse_form_data(body)
            name = form_data.get('name', '').strip()
            email = form_data.get('email', '').strip()
            subject = form_data.get('subject', '').strip()
            message = form_data.get('message', '').strip()

            if not name or not email or not message:
                return "<p style='color:red'>Error: name, email and message must be there.</p>", 400, {"Content-Type": "text/html; charset=utf-8"}

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO messages (name, email, subject, message)
                    VALUES (?, ?, ?, ?)
                ''', (name, email, subject, message))
                conn.commit()
                conn.close()

                return "<p style='color:green'> message saved successfully.</p>", 200, {"Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return f"<p style='color:red'>error in saving message: {e}</p>", 500, {"Content-Type": "text/html; charset=utf-8"}

        # add new user (users table)
        case "/users/new" if method == "GET":
            html = render_template("user_form.html")
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template user_form.html not found", 500, {"Content-Type": "text/html; charset=utf-8"}

        case "/users/new" if method == "POST":
            form_data = parse_form_data(body)
            username = form_data.get('username', '').strip()
            password_hash = form_data.get('password_hash', '').strip()  # in reality, it should be hashed
            email = form_data.get('email', '').strip()
            full_name = form_data.get('full_name', '').strip()
            role = form_data.get('role', 'analyst')

            if not username or not password_hash or not email:
                return "<p style='color:red'>error: username and password are a must.</p>", 400, {"Content-Type": "text/html; charset=utf-8"}

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, full_name, role, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                ''', (username, password_hash, email, full_name, role))
                conn.commit()
                conn.close()
                return "<p style='color:green'>new user successfully signed.</p>", 200, {"Content-Type": "text/html; charset=utf-8"}
            except sqlite3.IntegrityError as e:
                return f"<p style='color:red'>error: username or email is duplicate. ({e})</p>", 400, {"Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return f"<p style='color:red'>error signing user {e}</p>", 500, {"Content-Type": "text/html; charset=utf-8"}


        # add new product (products table)
        case "/products/new" if method == "GET":
            html = render_template("product_form.html")
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return "Template product_form.html not found", 500, {"Content-Type": "text/html; charset=utf-8"}

        case "/products/new" if method == "POST":
            form_data = parse_form_data(body)
            name = form_data.get('name', '').strip()
            description = form_data.get('description', '').strip()
            price = form_data.get('price', '')
            category = form_data.get('category', '')
            is_active = form_data.get('is_active', '1')

            if not name:
                return "<p style='color:red'>error: product name is a must.</p>", 400, {"Content-Type": "text/html; charset=utf-8"}

            # convert price to float or None
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
                return "<p style='color:green'>new product successfully added!</p>", 200, {"Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return f"<p style='color:red'>error when adding new product: {e}</p>", 500, {"Content-Type": "text/html; charset=utf-8"}

        # show database table information

        # show users list(users table)
        case "/admin/users":
            if method == "GET":
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, username, email, full_name, role, is_active, created_at FROM users')
                    users = cursor.fetchall()
                    conn.close()

                    html = render_template("users_list.html")
                    if html:
                        table_rows = ""
                        for user in users:
                            status_class = "bg-green-100 text-green-700" if user[
                                'is_active'] else "bg-red-100 text-red-700"
                            status_text = "فعال" if user['is_active'] else "غیرفعال"
                            table_rows += f"""
                            <tr class="border-b hover:bg-gray-50 transition-colors">
                                <td class="px-4 py-3 text-center">{user['id']}</td>
                                <td class="px-4 py-3 text-center font-medium">{user['username']}</td>
                                <td class="px-4 py-3 text-center text-gray-600">{user['email']}</td>
                                <td class="px-4 py-3 text-center">{user['full_name'] or '-'}</td>
                                <td class="px-4 py-3 text-center">
                                    <span class="px-2 py-1 bg-purple-100 text-purple-700 rounded-lg text-sm">{user['role']}</span>
                                </td>
                                <td class="px-4 py-3 text-center">
                                    <span class="px-3 py-1 rounded-full text-sm {status_class}">{status_text}</span>
                                </td>
                                <td class="px-4 py-3 text-center text-gray-500 text-sm">{user['created_at']}</td>
                                <td class="px-4 py-3 text-center">
                                    <a href="/weather_platform/admin/users/edit/1" 
                                       class="inline-block px-3 py-1 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition-colors">
                                        ✏️ ویرایش
                                    </a>
                                </td>
                            </tr>
                            """
                        html = html.replace("{{users_rows}}", table_rows)
                        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                except Exception as e:
                    return f"<p style='color:red'>error when adding new product: {e}</p>", 500, {
                        "Content-Type": "text/html; charset=utf-8"}

        # show weather data(weather_data table)
        case "/weather/list":
            if method == "GET":
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

                    html = render_template("weather_list.html")
                    if html:
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
                        html = html.replace("{{weather_rows}}", table_rows)
                        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                    return "Template weather_list.html not found", 500, {"Content-Type": "text/plain"}
                except Exception as e:
                    return f"<p style='color:red'>error when fetching weather information {e}</p>", 500, {
                        "Content-Type": "text/html; charset=utf-8"}

        # show analysis report (analysis_reports table)
        case "/reports/list":
            if method == "GET":
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

                    html = render_template("reports_list.html")
                    if html:
                        table_rows = ""
                        for report in reports:
                            table_rows += f"""
                            <tr>
                                <td>{report['id']}</td>
                                <td>{report['title']}</td>
                                <td>{report['report_type'] or '-'}</td>
                                <td>{report['start_date'] or '-'}</td>
                                <td>{report['end_date'] or '-'}</td>
                                <td>{report['region'] or '-'}</td>
                                <td>{"عمومی" if report['is_public'] else "خصوصی"}</td>
                                <td>{report['view_count']}</td>
                                <td>{report['created_at']}</td>
                            </tr>
                            """
                        html = html.replace("{{reports_rows}}", table_rows)
                        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                    return "Template reports_list.html not found", 500, {"Content-Type": "text/plain"}
                except Exception as e:
                    return f"<p style='color:red'>error when fetching logs: {e}</p>", 500, {
                        "Content-Type": "text/html; charset=utf-8"}

        # show messages (messages table)
        case "/admin/messages":
            if method == "GET":
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        'SELECT id, name, email, subject, message, is_read, created_at FROM messages ORDER BY created_at DESC')
                    messages = cursor.fetchall()
                    conn.close()

                    html = render_template("messages_list.html")
                    if html:
                        table_rows = ""
                        for msg in messages:
                            status_class = "bg-green-100 text-green-700" if msg[
                                'is_read'] else "bg-orange-100 text-orange-700"
                            status_text = "خوانده شده" if msg['is_read'] else "خوانده نشده"
                            short_message = msg['message'][:50] + "..." if len(msg['message']) > 50 else msg['message']
                            table_rows += f"""
                            <tr class="border-b hover:bg-gray-50 transition-colors">
                                <td class="px-4 py-3 text-center">{msg['id']}</td>
                                <td class="px-4 py-3 text-center font-medium">{msg['name']}</td>
                                <td class="px-4 py-3 text-center text-gray-600">{msg['email']}</td>
                                <td class="px-4 py-3 text-center">{msg['subject'] or '-'}</td>
                                <td class="px-4 py-3 text-right text-gray-600 max-w-xs text-sm">{short_message}</td>
                                <td class="px-4 py-3 text-center">
                                    <span class="px-3 py-1 rounded-full text-sm {status_class}">{status_text}</span>
                                </td>
                                <td class="px-4 py-3 text-center text-gray-500 text-sm">{msg['created_at']}</td>
                            </tr>
                            """
                        html = html.replace("{{messages_rows}}", table_rows)
                        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                    return "Template messages_list.html not found", 500, {"Content-Type": "text/plain"}
                except Exception as e:
                    return f"<p style='color:red'>error when fetching messages: {e}</p>", 500, {
                        "Content-Type": "text/html; charset=utf-8"}

        # show products (products table)
        case "/products/list":
            if method == "GET":
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, name, description, price, category, is_active, created_at FROM products')
                    products = cursor.fetchall()
                    conn.close()

                    html = render_template("products_list.html")
                    if html:
                        table_rows = ""
                        for product in products:
                            status_class = "bg-green-100 text-green-700" if product[
                                'is_active'] else "bg-red-100 text-red-700"
                            status_text = "فعال" if product['is_active'] else "غیرفعال"
                            price_display = f"{product['price']:,.0f}" if product['price'] else "-"
                            table_rows += f"""
                            <tr class="border-b hover:bg-gray-50 transition-colors">
                                <td class="px-4 py-3 text-center">{product['id']}</td>
                                <td class="px-4 py-3 text-center font-medium">{product['name']}</td>
                                <td class="px-4 py-3 text-right text-gray-600 max-w-xs">{product['description'] or '-'}</td>
                                <td class="px-4 py-3 text-center font-bold text-teal-600">{price_display}</td>
                                <td class="px-4 py-3 text-center">
                                    <span class="px-2 py-1 bg-gray-100 text-gray-700 rounded-lg text-sm">{product['category'] or '-'}</span>
                                </td>
                                <td class="px-4 py-3 text-center">
                                    <span class="px-3 py-1 rounded-full text-sm {status_class}">{status_text}</span>
                                </td>
                                <td class="px-4 py-3 text-center text-gray-500 text-sm">{product['created_at']}</td>
                                <td class="px-4 py-3 text-center">
                                    <a href="/weather_platform/products/edit/1" 
                                       class="inline-block px-3 py-1 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition-colors">
                                        ✏️ ویرایش
                                    </a>
                                </td>
                            </tr>
                            """
                        html = html.replace("{{products_rows}}", table_rows)
                        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                    return "Template products_list.html not found", 500, {"Content-Type": "text/plain"}
                except Exception as e:
                    return f"<p style='color:red'>error when fetching products: {e}</p>", 500, {
                        "Content-Type": "text/html; charset=utf-8"}

        # show products catalog (card view)
        case "/products/catalog":
            if method == "GET":
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

                    html = render_template("catalog.html")
                    if html:
                        catalog_cards = ""
                        for product in products:
                            # تعیین آیکون بر اساس دسته‌بندی
                            category_icon = "📦"
                            category_name = product['category'] or 'متفرقه'
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
                            <div class="product-card bg-white rounded-2xl shadow-lg overflow-hidden" 
                                 data-title="{product['name']}" 
                                 data-description="{product['description'] or ''}" 
                                 data-category="{product['category'] or 'other'}">
                                <div class="bg-gradient-to-r from-purple-500 to-indigo-600 h-40 flex items-center justify-center">
                                    <div class="text-7xl">{category_icon}</div>
                                </div>
                                <div class="p-6">
                                    <h3 class="text-xl font-bold text-gray-800 mb-2">{product['name']}</h3>
                                    <span class="inline-block px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm mb-3">
                                        {category_icon} {category_name}
                                    </span>
                                    <p class="text-gray-600 text-sm leading-relaxed mb-4 min-h-[80px]">
                                        {product['description'] or 'توضیحاتی برای این محصول ثبت نشده است'}
                                    </p>
                                    <div class="text-2xl font-bold text-purple-600 mb-4">{price_display} <span class="text-sm text-gray-500">تومان</span></div>
                                    <div class="flex gap-3">
                                        <button class="flex-1 bg-purple-600 text-white py-2 rounded-xl hover:bg-purple-700 transition-all duration-300">
                                            خرید
                                        </button>
                                        <button class="flex-1 border border-purple-600 text-purple-600 py-2 rounded-xl hover:bg-purple-50 transition-all duration-300">
                                            اطلاعات بیشتر
                                        </button>
                                    </div>
                                </div>
                            </div>
                            '''
                        html = html.replace("{{catalog_cards}}", catalog_cards)
                        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                    return "Template catalog.html not found", 500, {"Content-Type": "text/plain"}
                except Exception as e:
                    return f"<p style='color:red'>error when fetching products for catalog: {e}</p>", 500, {
                        "Content-Type": "text/html; charset=utf-8"}

        # Edit user (GET form + POST update)
        case "/admin/users/edit/1" if method == "GET":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id, username, email, full_name, role, is_active FROM users WHERE id = 1')
                user = cursor.fetchone()
                conn.close()

                if not user:
                    return "<p style='color:red'>کاربر با شناسه 1 یافت نشد</p>", 404, {
                        "Content-Type": "text/html; charset=utf-8"}

                html = render_template("user_edit.html")
                if html:
                    # جایگزینی داده‌های کاربر در فرم
                    html = html.replace("{{user_id}}", str(user['id']))
                    html = html.replace("{{username}}", user['username'])
                    html = html.replace("{{email}}", user['email'])
                    html = html.replace("{{full_name}}", user['full_name'] or '')
                    html = html.replace("{{role}}", user['role'])
                    html = html.replace("{{is_active_checked}}", 'checked' if user['is_active'] else '')
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return "Template user_edit.html not found", 500, {"Content-Type": "text/plain"}
            except Exception as e:
                return f"<p style='color:red'>خطا: {e}</p>", 500, {"Content-Type": "text/html; charset=utf-8"}

        case "/admin/users/edit/1" if method == "POST":
            form_data = parse_form_data(body)
            username = form_data.get('username', '').strip()
            email = form_data.get('email', '').strip()
            full_name = form_data.get('full_name', '').strip()
            role = form_data.get('role', 'analyst')
            is_active = 1 if form_data.get('is_active') == 'on' else 0

            if not username or not email:
                return "<p style='color:red'>نام کاربری و ایمیل الزامی هستند</p>", 400, {
                    "Content-Type": "text/html; charset=utf-8"}

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               UPDATE users
                               SET username  = ?,
                                   email     = ?,
                                   full_name = ?,
                                   role      = ?,
                                   is_active = ?
                               WHERE id = 1
                               ''', (username, email, full_name, role, is_active))
                conn.commit()
                conn.close()

                return """
                <!DOCTYPE html>
                <html dir="rtl" lang="fa">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-gradient-to-br from-purple-600 to-indigo-700 min-h-screen flex items-center justify-center">
                    <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md text-center">
                        <div class="text-6xl mb-4">✅</div>
                        <h2 class="text-2xl font-bold text-gray-800 mb-4">اطلاعات کاربر با موفقیت ویرایش شد</h2>
                        <p class="text-gray-600 mb-6">کاربر با شناسه 1 به روز رسانی شد</p>
                        <div class="flex gap-3 justify-center">
                            <a href="/weather_platform/admin/users" class="px-6 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700">بازگشت به لیست کاربران</a>
                            <a href="/weather_platform/dashboard" class="px-6 py-2 bg-gray-600 text-white rounded-xl hover:bg-gray-700">داشبورد</a>
                        </div>
                    </div>
                </body>
                </html>
                """, 200, {"Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return f"<p style='color:red'>خطا در ویرایش کاربر: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # Edit product (GET form + POST update)
        case "/products/edit/1" if method == "GET":
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id, name, description, price, category, is_active FROM products WHERE id = 1')
                product = cursor.fetchone()
                conn.close()

                if not product:
                    return "<p style='color:red'>محصول با شناسه 1 یافت نشد</p>", 404, {
                        "Content-Type": "text/html; charset=utf-8"}

                html = render_template("product_edit.html")
                if html:
                    # جایگزینی داده‌های محصول در فرم
                    html = html.replace("{{product_id}}", str(product['id']))
                    html = html.replace("{{name}}", product['name'])
                    html = html.replace("{{description}}", product['description'] or '')
                    html = html.replace("{{price}}", str(product['price']) if product['price'] else '')
                    html = html.replace("{{category}}", product['category'] or '')
                    html = html.replace("{{is_active_checked}}", 'checked' if product['is_active'] else '')
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return "Template product_edit.html not found", 500, {"Content-Type": "text/plain"}
            except Exception as e:
                return f"<p style='color:red'>خطا: {e}</p>", 500, {"Content-Type": "text/html; charset=utf-8"}

        case "/products/edit/1" if method == "POST":
            form_data = parse_form_data(body)
            name = form_data.get('name', '').strip()
            description = form_data.get('description', '').strip()
            price = form_data.get('price', '')
            category = form_data.get('category', '')
            is_active = 1 if form_data.get('is_active') == 'on' else 0

            if not name:
                return "<p style='color:red'>نام محصول الزامی است</p>", 400, {
                    "Content-Type": "text/html; charset=utf-8"}

            # تبدیل قیمت به float یا None
            try:
                price_float = float(price) if price else None
            except ValueError:
                price_float = None

            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               UPDATE products
                               SET name        = ?,
                                   description = ?,
                                   price       = ?,
                                   category    = ?,
                                   is_active   = ?
                               WHERE id = 1
                               ''', (name, description, price_float, category, is_active))
                conn.commit()
                conn.close()

                return """
                <!DOCTYPE html>
                <html dir="rtl" lang="fa">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-gradient-to-br from-teal-500 to-green-600 min-h-screen flex items-center justify-center">
                    <div class="bg-white rounded-2xl shadow-2xl p-8 max-w-md text-center">
                        <div class="text-6xl mb-4">✅</div>
                        <h2 class="text-2xl font-bold text-gray-800 mb-4">اطلاعات محصول با موفقیت ویرایش شد</h2>
                        <p class="text-gray-600 mb-6">محصول با شناسه 1 به روز رسانی شد</p>
                        <div class="flex gap-3 justify-center">
                            <a href="/weather_platform/products/list" class="px-6 py-2 bg-teal-600 text-white rounded-xl hover:bg-teal-700">بازگشت به لیست محصولات</a>
                            <a href="/weather_platform/dashboard" class="px-6 py-2 bg-gray-600 text-white rounded-xl hover:bg-gray-700">داشبورد</a>
                        </div>
                    </div>
                </body>
                </html>
                """, 200, {"Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return f"<p style='color:red'>خطا در ویرایش محصول: {e}</p>", 500, {
                    "Content-Type": "text/html; charset=utf-8"}

        # main dashboard with link to every table
        case "/dashboard":
            if method == "GET":
                html = render_template("dashboard.html")
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return "Template dashboard.html not found", 500, {"Content-Type": "text/plain"}

        # JSON example

        case "/api/status":

            data = {"project": "weather_platform", "status": "ok"}

            return (json.dumps(data, ensure_ascii=False), 200,

                    {"Content-Type": "application/json"})

        # POST echo example

        case "/api/echo" if method == "POST":

            data = {"received": body, "length": len(body)}

            return (json.dumps(data, ensure_ascii=False), 200,

                    {"Content-Type": "application/json"})

        # invalid route

        case _:

            return ("Not Found (inside weather_platform)", 404,

                {"Content-Type": "text/plain; charset=utf-8"})

