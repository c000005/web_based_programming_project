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
            return render_error_page(500, "Template index.html not found")

        # Contact page
        elif path == "/contact":
            html = render_template("contact.html", {"title": "تماس با ما"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template contact.html not found")

        # Register page
        elif path == "/register":
            html = render_template("register.html", {"title": "ثبت‌نام"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template register.html not found")

        # Add weather form
        elif path == "/add_weather":
            html = render_template("add_weather.html", {"title": "ثبت داده هواشناسی"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template add_weather.html not found")

        # About page
        elif path == "/about":
            html = render_template("about.html", {"title": "درباره ما"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template about.html not found")

        # New message form
        elif path == "/messages/new":
            html = render_template("message_form.html", {"title": "ارسال پیام جدید"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template message_form.html not found")

        # View single message
        elif path.startswith("/messages/view/"):
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

        # New user form
        elif path == "/users/new":
            html = render_template("user_form.html", {"title": "ثبت نام کاربر جدید"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template user_form.html not found")

        # Edit user
        elif path.startswith("/admin/users/edit/"):
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

        # New product form
        elif path == "/products/new":
            html = render_template("product_form.html", {"title": "افزودن محصول جدید"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template product_form.html not found")

        # Edit product
        elif path.startswith("/products/edit/"):
            try:
                product_id = int(path.split("/")[-1])
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, name, description, price, category, is_active FROM products WHERE id = ?',
                    (product_id,))
                product = cursor.fetchone()
                conn.close()

                if not product:
                    return render_error_page(404, f"محصول با شناسه {product_id} یافت نشد")

                html = render_template("product_edit.html", {
                    "title": "ویرایش محصول",
                    "product_id": product_id,
                    "name": product['name'],
                    "description": product['description'] or '',
                    "price": product['price'] if product['price'] is not None else '',
                    "category": product['category'] or '',
                    "is_active_checked": "checked" if product['is_active'] else ""
                })
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return render_error_page(500, "Template product_edit.html not found")
            except ValueError:
                return render_error_page(404, "شناسه نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در دریافت محصول: {e}")

        # View single product
        elif path.startswith("/products/view/"):
            try:
                product_id = int(path.split("/")[-1])
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT id, name, description, price, category, is_active, created_at FROM products WHERE id = ?',
                    (product_id,))
                product = cursor.fetchone()
                conn.close()

                if not product:
                    return render_error_page(404, f"محصول با شناسه {product_id} یافت نشد")

                html = render_template("product_view.html", {
                    "title": "نمایش محصول",
                    "product_id": product_id,
                    "name": product['name'],
                    "description": product['description'] or 'توضیحی ثبت نشده است',
                    "price": f"{product['price']:,.0f}" if product['price'] is not None else "تماس بگیرید",
                    "category": product['category'] or 'سایر',
                    "is_active_text": "✅ فعال" if product['is_active'] else "❌ غیرفعال",
                    "created_at": product['created_at']
                })
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return render_error_page(500, "Template product_view.html not found")
            except ValueError:
                return render_error_page(404, "شناسه نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در دریافت محصول: {e}")

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
                        <td>
                            <a href="/weather_platform/admin/users/edit/{user['id']}" class="btn btn-sm btn-primary">✏️ ویرایش</a>
                        </td>
                    </tr>
                    """

                html = render_template("users_list.html", {"title": "لیست کاربران", "users_rows": table_rows})
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return render_error_page(500, "Template users_list.html not found")
            except Exception as e:
                return render_error_page(500, f"خطا در دریافت کاربران: {e}")

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
                return render_error_page(500, "Template weather_list.html not found")
            except Exception as e:
                return render_error_page(500, f"خطا در دریافت داده‌های هواشناسی: {e}")

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
                        <td>
                            <a href="/weather_platform/products/edit/{product['id']}" class="btn btn-sm btn-primary">✏️ ویرایش</a>
                            <a href="/weather_platform/products/view/{product['id']}" class="btn btn-sm btn-info">👁️ مشاهده</a>
                        </td>
                    </tr>
                    """

                html = render_template("products_list.html", {"title": "لیست محصولات", "products_rows": table_rows})
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return render_error_page(500, "Template products_list.html not found")
            except Exception as e:
                return render_error_page(500, f"خطا در دریافت محصولات: {e}")

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
                                <a href="/weather_platform/products/view/{product['id']}" class="btn btn-primary">مشاهده</a>
                                <a href="/weather_platform/products/edit/{product['id']}" class="btn btn-secondary">ویرایش</a>
                            </div>
                        </div>
                    </div>
                    '''

                html = render_template("catalog.html", {"title": "کاتالوگ محصولات", "catalog_cards": catalog_cards})
                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return render_error_page(500, "Template catalog.html not found")
            except Exception as e:
                return render_error_page(500, f"خطا در دریافت کاتالوگ: {e}")

        # Dashboard
        elif path == "/dashboard":
            html = render_template("dashboard.html", {"title": "داشبورد مدیریت"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template dashboard.html not found")

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
                return render_error_page(500, "Template reports_list.html not found")
            except Exception as e:
                return render_error_page(500, f"خطا در دریافت گزارش‌ها: {e}")
        # ========== سبد خرید (Cart) ==========
        # مشاهده سبد خرید
        elif path == "/cart":
            try:
                user_id = 1  # کاربر فعال فعلی
                conn = get_db_connection()
                cursor = conn.cursor()

                # استفاده از JOIN برای دریافت اطلاعات محصولات همراه با تعداد
                cursor.execute('''
                               SELECT c.id   as cart_id,
                                      c.quantity,
                                      c.added_at,
                                      p.id   as product_id,
                                      p.name as product_name,
                                      p.description,
                                      p.price,
                                      p.category,
                                      p.is_active
                               FROM cart_items c
                                        JOIN products p ON c.product_id = p.id
                               WHERE c.user_id = ?
                               ORDER BY c.added_at DESC
                               ''', (user_id,))

                cart_items = cursor.fetchall()
                conn.close()

                # محاسبه مجموع قیمت
                total_price = sum(item['price'] * item['quantity'] for item in cart_items if item['price'])

                # ساخت جدول HTML
                table_rows = ""
                for item in cart_items:
                    price_display = f"{item['price']:,.0f}" if item['price'] else "رایگان"
                    total_item_price = f"{(item['price'] * item['quantity']):,.0f}" if item['price'] else "رایگان"
                    table_rows += f"""
                    <tr>
                        <td>{item['product_id']}</td>
                        <td><strong>{item['product_name']}</strong></td>
                        <td>{price_display} تومان</td>
                        <td>
                            <form action="/weather_platform/cart/update/{item['cart_id']}" method="POST" style="display: inline;">
                                <input type="number" name="quantity" value="{item['quantity']}" min="1" max="99" style="width: 60px; padding: 5px;">
                                <button type="submit" class="btn btn-sm btn-primary">بروزرسانی</button>
                            </form>
                        </td>
                        <td>{total_item_price} تومان</td>
                        <td>
                            <a href="/weather_platform/cart/remove/{item['cart_id']}" class="btn btn-sm btn-danger" onclick="return confirm('آیا از حذف این آیتم اطمینان دارید؟')">🗑️ حذف</a>
                        </td>
                    </tr>
                    """

                html = render_template("cart.html", {
                    "title": "سبد خرید",
                    "cart_items": table_rows,
                    "total_price": f"{total_price:,.0f}" if total_price else "0",
                    "item_count": len(cart_items)
                })

                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return render_error_page(500, "Template cart.html not found")

            except Exception as e:
                return render_error_page(500, f"خطا در دریافت سبد خرید: {e}")

        # ========== علاقمندی‌ها (Wishlist) ==========
        # مشاهده لیست علاقمندی‌ها
        elif path == "/wishlist":
            try:
                user_id = 1  # کاربر فعال فعلی
                conn = get_db_connection()
                cursor = conn.cursor()

                # استفاده از JOIN برای دریافت اطلاعات محصولات
                cursor.execute('''
                               SELECT w.id   as wish_id,
                                      w.added_at,
                                      p.id   as product_id,
                                      p.name as product_name,
                                      p.description,
                                      p.price,
                                      p.category,
                                      p.is_active
                               FROM wishlist_items w
                                        JOIN products p ON w.product_id = p.id
                               WHERE w.user_id = ?
                               ORDER BY w.added_at DESC
                               ''', (user_id,))

                wishlist_items = cursor.fetchall()
                conn.close()

                # ساخت کارت‌های نمایش
                wishlist_cards = ""
                for item in wishlist_items:
                    price_display = f"{item['price']:,.0f}" if item['price'] else "رایگان"
                    category_icon = "📦"
                    if item['category'] == 'subscription':
                        category_icon = "📅"
                    elif item['category'] == 'api_access':
                        category_icon = "🔌"
                    elif item['category'] == 'custom_report':
                        category_icon = "📊"

                    wishlist_cards += f'''
                    <div class="wishlist-card">
                        <div class="flex items-center justify-between p-4 border-b">
                            <div>
                                <h3 class="font-bold text-lg">{item['product_name']}</h3>
                                <span class="text-sm text-gray-600">{category_icon} {item['category'] or 'سایر'}</span>
                            </div>
                            <div class="text-lg font-bold text-green-600">{price_display} تومان</div>
                        </div>
                        <div class="p-4">
                            <p class="text-gray-600 text-sm">{item['description'] or 'توضیحی ثبت نشده است'}</p>
                            <div class="mt-4 flex gap-2">
                                <a href="/weather_platform/products/view/{item['product_id']}" class="btn btn-sm btn-info">👁️ مشاهده</a>
                                <a href="/weather_platform/cart/add/{item['product_id']}" class="btn btn-sm btn-success">🛒 افزودن به سبد</a>
                                <a href="/weather_platform/wishlist/remove/{item['wish_id']}" class="btn btn-sm btn-danger" onclick="return confirm('آیا از حذف این آیتم از علاقمندی‌ها اطمینان دارید؟')">❤️ حذف</a>
                            </div>
                        </div>
                    </div>
                    '''

                html = render_template("wishlist.html", {
                    "title": "علاقمندی‌ها",
                    "wishlist_cards": wishlist_cards,
                    "item_count": len(wishlist_items)
                })

                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return render_error_page(500, "Template wishlist.html not found")

            except Exception as e:
                return render_error_page(500, f"خطا در دریافت علاقمندی‌ها: {e}")

        # ========== نظرات محصولات ==========
        # مشاهده نظرات یک محصول (در صفحه نمایش محصول)
        elif path.startswith("/products/view/"):
            try:
                product_id = int(path.split("/")[-1])
                conn = get_db_connection()
                cursor = conn.cursor()

                # دریافت اطلاعات محصول
                cursor.execute(
                    'SELECT id, name, description, price, category, is_active, created_at FROM products WHERE id = ?',
                    (product_id,))
                product = cursor.fetchone()

                if not product:
                    conn.close()
                    return render_error_page(404, f"محصول با شناسه {product_id} یافت نشد")

                # دریافت نظرات محصول با استفاده از JOIN
                cursor.execute('''
                               SELECT c.id as comment_id,
                                      c.comment,
                                      c.rating,
                                      c.created_at,
                                      u.id as user_id,
                                      u.username,
                                      u.full_name
                               FROM product_comments c
                                        JOIN users u ON c.user_id = u.id
                               WHERE c.product_id = ?
                                 AND c.is_approved = 1
                               ORDER BY c.created_at DESC
                               ''', (product_id,))

                comments = cursor.fetchall()
                conn.close()

                # ساخت نظرات HTML
                comments_html = ""
                if comments:
                    for comment in comments:
                        stars = "⭐" * (comment['rating'] if comment['rating'] else 0)
                        user_name = comment['full_name'] or comment['username']
                        comments_html += f'''
                        <div class="comment-item border-b pb-4 mb-4">
                            <div class="flex justify-between items-center">
                                <div>
                                    <strong>{user_name}</strong>
                                    <span class="text-yellow-500">{stars}</span>
                                </div>
                                <span class="text-sm text-gray-500">{comment['created_at']}</span>
                            </div>
                            <p class="mt-2 text-gray-700">{comment['comment']}</p>
                        </div>
                        '''
                else:
                    comments_html = '<p class="text-gray-500 text-center py-4">هنوز نظری برای این محصول ثبت نشده است.</p>'

                # نمایش محصول با نظرات
                html = render_template("product_view.html", {
                    "title": "نمایش محصول",
                    "product_id": product_id,
                    "name": product['name'],
                    "description": product['description'] or 'توضیحی ثبت نشده است',
                    "price": f"{product['price']:,.0f}" if product['price'] is not None else "تماس بگیرید",
                    "category": product['category'] or 'سایر',
                    "is_active_text": "✅ فعال" if product['is_active'] else "❌ غیرفعال",
                    "created_at": product['created_at'],
                    "comments": comments_html,
                    "comments_count": len(comments)
                })

                if html:
                    return html, 200, {"Content-Type": "text/html; charset=utf-8"}
                return render_error_page(500, "Template product_view.html not found")

            except ValueError:
                return render_error_page(404, "شناسه نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در دریافت محصول: {e}")
        # API status
        elif path == "/api/status":
            data = {"project": "weather_platform", "status": "ok"}
            return json.dumps(data, ensure_ascii=False), 200, {"Content-Type": "application/json"}

        # 404
        else:
            return render_error_page(404, f"صفحه {path} یافت نشد")

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
                return """<p style='color:green'>✅ Message saved successfully.</p>""", 200, {
                    "Content-Type": "text/html; charset=utf-8"}
            except Exception as e:
                return render_error_page(500, f"خطا در ذخیره پیام: {e}")

        # Handle user registration
        elif path == "/register":
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

        # Handle product addition
        elif path == "/products/new":
            name = form_data.get('name', '').strip()
            description = form_data.get('description', '').strip()
            price = form_data.get('price', '')
            category = form_data.get('category', '')
            is_active = form_data.get('is_active', '1')

            if not name:
                return render_error_page(400, "نام محصول الزامی است")

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
                return render_error_page(500, f"خطا در افزودن محصول: {e}")

        # Handle user edit
        elif path.startswith("/admin/users/edit/"):
            try:
                user_id = int(path.split("/")[-1])
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
                return "<p style='color:green'>✅ User updated successfully!</p>", 200, {
                    "Content-Type": "text/html; charset=utf-8"}
            except ValueError:
                return render_error_page(400, "شناسه نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در بروزرسانی کاربر: {e}")

        # Handle product edit
        elif path.startswith("/products/edit/"):
            try:
                product_id = int(path.split("/")[-1])
                name = form_data.get('name', '').strip()
                description = form_data.get('description', '').strip()
                price = form_data.get('price', '')
                category = form_data.get('category', '')
                is_active = form_data.get('is_active', '0')

                if not name:
                    return render_error_page(400, "نام محصول الزامی است")

                try:
                    price_float = float(price) if price else None
                except ValueError:
                    price_float = None

                is_active_int = 1 if is_active == '1' else 0

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               UPDATE products
                               SET name = ?, description = ?, price = ?, category = ?, is_active = ?
                               WHERE id = ?
                               ''', (name, description, price_float, category, is_active_int, product_id))

                if cursor.rowcount == 0:
                    conn.close()
                    return render_error_page(404, f"محصول با شناسه {product_id} یافت نشد")

                conn.commit()
                conn.close()
                return "<p style='color:green'>✅ Product updated successfully!</p>", 200, {
                    "Content-Type": "text/html; charset=utf-8"}
            except ValueError:
                return render_error_page(400, "شناسه نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در بروزرسانی محصول: {e}")

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
                return render_error_page(400, "کد ایستگاه، نام شهر، کشور و تاریخ ثبت الزامی هستند")

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
                return render_error_page(500, f"خطا در ذخیره داده هواشناسی: {e}")
        # ========== سبد خرید (Cart) ==========
        # افزودن به سبد خرید
        elif path.startswith("/cart/add/"):
            try:
                product_id = int(path.split("/")[-1])
                user_id = 1  # کاربر فعال فعلی

                # بررسی وجود محصول
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id, is_active FROM products WHERE id = ?', (product_id,))
                product = cursor.fetchone()

                if not product:
                    conn.close()
                    return render_error_page(404, "محصول مورد نظر یافت نشد")

                if not product['is_active']:
                    conn.close()
                    return render_error_page(400, "این محصول غیرفعال است")

                # افزودن به سبد خرید یا افزایش تعداد
                cursor.execute('''
                               INSERT INTO cart_items (user_id, product_id, quantity)
                               VALUES (?, ?, 1) ON CONFLICT(user_id, product_id) 
                    DO
                               UPDATE SET quantity = quantity + 1
                               ''', (user_id, product_id))

                conn.commit()
                conn.close()

                return """
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl mb-4">
                    <strong>✅ موفق!</strong> محصول به سبد خرید اضافه شد.
                    <br>
                    <a href="/weather_platform/cart" class="text-green-800 underline">مشاهده سبد خرید</a>
                </div>
                """, 200, {"Content-Type": "text/html; charset=utf-8"}

            except ValueError:
                return render_error_page(400, "شناسه محصول نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در افزودن به سبد خرید: {e}")

        # بروزرسانی تعداد در سبد خرید
        elif path.startswith("/cart/update/"):
            try:
                cart_id = int(path.split("/")[-1])
                quantity = int(form_data.get('quantity', 1))

                if quantity < 1:
                    quantity = 1
                if quantity > 99:
                    quantity = 99

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                               UPDATE cart_items
                               SET quantity = ?
                               WHERE id = ?
                                 AND user_id = 1
                               ''', (quantity, cart_id))

                if cursor.rowcount == 0:
                    conn.close()
                    return render_error_page(404, "آیتم مورد نظر در سبد خرید یافت نشد")

                conn.commit()
                conn.close()

                return """
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl mb-4">
                    ✅ تعداد آیتم بروزرسانی شد.
                    <br>
                    <a href="/weather_platform/cart" class="text-green-800 underline">بازگشت به سبد خرید</a>
                </div>
                """, 200, {"Content-Type": "text/html; charset=utf-8"}

            except ValueError:
                return render_error_page(400, "مقادیر نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در بروزرسانی سبد خرید: {e}")

        # حذف از سبد خرید
        elif path.startswith("/cart/remove/"):
            try:
                cart_id = int(path.split("/")[-1])

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cart_items WHERE id = ? AND user_id = 1', (cart_id,))

                if cursor.rowcount == 0:
                    conn.close()
                    return render_error_page(404, "آیتم مورد نظر در سبد خرید یافت نشد")

                conn.commit()
                conn.close()

                return """
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl mb-4">
                    ✅ آیتم از سبد خرید حذف شد.
                    <br>
                    <a href="/weather_platform/cart" class="text-green-800 underline">بازگشت به سبد خرید</a>
                </div>
                """, 200, {"Content-Type": "text/html; charset=utf-8"}

            except ValueError:
                return render_error_page(400, "شناسه نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در حذف از سبد خرید: {e}")

        # ========== علاقمندی‌ها (Wishlist) ==========
        # افزودن به علاقمندی‌ها
        elif path.startswith("/wishlist/add/"):
            try:
                product_id = int(path.split("/")[-1])
                user_id = 1  # کاربر فعال فعلی

                # بررسی وجود محصول
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
                product = cursor.fetchone()

                if not product:
                    conn.close()
                    return render_error_page(404, "محصول مورد نظر یافت نشد")

                # افزودن به علاقمندی‌ها
                cursor.execute('''
                               INSERT
                               OR IGNORE INTO wishlist_items (user_id, product_id)
                    VALUES (?, ?)
                               ''', (user_id, product_id))

                conn.commit()
                conn.close()

                return """
                <div class="bg-pink-100 border border-pink-400 text-pink-700 px-4 py-3 rounded-xl mb-4">
                    ❤️ محصول به لیست علاقمندی‌ها اضافه شد.
                    <br>
                    <a href="/weather_platform/wishlist" class="text-pink-800 underline">مشاهده علاقمندی‌ها</a>
                </div>
                """, 200, {"Content-Type": "text/html; charset=utf-8"}

            except ValueError:
                return render_error_page(400, "شناسه محصول نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در افزودن به علاقمندی‌ها: {e}")

        # حذف از علاقمندی‌ها
        elif path.startswith("/wishlist/remove/"):
            try:
                wish_id = int(path.split("/")[-1])

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM wishlist_items WHERE id = ? AND user_id = 1', (wish_id,))

                if cursor.rowcount == 0:
                    conn.close()
                    return render_error_page(404, "آیتم مورد نظر در علاقمندی‌ها یافت نشد")

                conn.commit()
                conn.close()

                return """
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl mb-4">
                    ✅ آیتم از علاقمندی‌ها حذف شد.
                    <br>
                    <a href="/weather_platform/wishlist" class="text-green-800 underline">بازگشت به علاقمندی‌ها</a>
                </div>
                """, 200, {"Content-Type": "text/html; charset=utf-8"}

            except ValueError:
                return render_error_page(400, "شناسه نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در حذف از علاقمندی‌ها: {e}")

        # ========== نظرات محصولات ==========
        # افزودن نظر برای محصول
        elif path.startswith("/products/comment/"):
            try:
                product_id = int(path.split("/")[-1])
                user_id = 1  # کاربر فعال فعلی
                comment = form_data.get('comment', '').strip()
                rating = form_data.get('rating', 3)

                if not comment:
                    return render_error_page(400, "متن نظر الزامی است")

                if len(comment) < 5:
                    return render_error_page(400, "متن نظر باید حداقل 5 کاراکتر باشد")

                try:
                    rating_int = int(rating)
                    if rating_int < 1 or rating_int > 5:
                        rating_int = 3
                except ValueError:
                    rating_int = 3

                conn = get_db_connection()
                cursor = conn.cursor()

                # بررسی وجود محصول
                cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
                if not cursor.fetchone():
                    conn.close()
                    return render_error_page(404, "محصول مورد نظر یافت نشد")

                # ثبت نظر
                cursor.execute('''
                               INSERT INTO product_comments (product_id, user_id, comment, rating, is_approved)
                               VALUES (?, ?, ?, ?, 1)
                               ''', (product_id, user_id, comment, rating_int))

                conn.commit()
                conn.close()

                return f"""
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded-xl mb-4">
                    ✅ نظر شما با موفقیت ثبت شد.
                    <br>
                    <a href="/weather_platform/products/view/{product_id}" class="text-green-800 underline">بازگشت به صفحه محصول</a>
                </div>
                """, 200, {"Content-Type": "text/html; charset=utf-8"}

            except ValueError:
                return render_error_page(400, "شناسه محصول نامعتبر")
            except Exception as e:
                return render_error_page(500, f"خطا در ثبت نظر: {e}")
    # Method not allowed
    return render_error_page(405, "روش غیرمجاز")


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