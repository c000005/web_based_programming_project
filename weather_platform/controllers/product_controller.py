# web_based_programming_project/weather_platform/controllers/product_controller.py

import sqlite3
from .base_controller import render_template, render_error_page, get_db_connection, parse_form_data
import settings


def get_all_products():
    """Get all active products"""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE is_deleted = 0 ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product(product_id):
    """Get a single product by ID"""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ? AND is_deleted = 0', (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(data):
    """Add a new product"""
    name = data.get('name', [''])[0]
    price = data.get('price', ['0'])[0]
    description = data.get('description', [''])[0]

    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO products (name, price, description)
                   VALUES (?, ?, ?)
                   ''', (name, price, description))
    conn.commit()
    conn.close()

    return True


def update_product(product_id, data):
    """Update a product"""
    name = data.get('name', [''])[0]
    price = data.get('price', ['0'])[0]
    description = data.get('description', [''])[0]

    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
                   UPDATE products
                   SET name        = ?,
                       price       = ?,
                       description = ?
                   WHERE id = ?
                   ''', (name, price, description, product_id))
    conn.commit()
    conn.close()

    return True


def delete_product(product_id):
    """Soft delete a product"""
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET is_deleted = 1 WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

    return True


def handle_products_catalog(headers):
    """Show product catalog with cards"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''SELECT id, name, description, price, category, is_active
                          FROM products
                          WHERE is_active = 1
                          ORDER BY id DESC''')
        products = cursor.fetchall()
        conn.close()

        catalog_cards = ""
        for p in products:
            price_display = f"{p['price']:,.0f}" if p['price'] else "رایگان"
            category_icon = "📦"
            if p['category'] == 'subscription':
                category_icon = "📅"
            elif p['category'] == 'api_access':
                category_icon = "🔌"
            elif p['category'] == 'custom_report':
                category_icon = "📊"

            catalog_cards += f'''
            <div class="product-card" data-title="{p['name'].lower()}" 
                 data-description="{p['description'].lower() if p['description'] else ''}" 
                 data-category="{p['category'] or ''}">
                <div class="product-image">{category_icon}</div>
                <div class="product-body">
                    <h3>{p['name']}</h3>
                    <span class="category">{p['category'] or 'سایر'}</span>
                    <p class="description">{p['description'] or 'توضیحی ثبت نشده'}</p>
                    <div class="price">{price_display} تومان</div>
                    <div class="actions">
                        <a href="/weather_platform/products/view/{p['id']}" class="btn btn-primary">👁️ مشاهده</a>
                        <a href="/weather_platform/cart/add/{p['id']}" class="btn btn-success">🛒 خرید</a>
                        <a href="/weather_platform/wishlist/add/{p['id']}" class="btn btn-danger">❤️</a>
                    </div>
                </div>
            </div>
            '''

        html = render_template("catalog.html", {
            "title": "کاتالوگ محصولات",
            "catalog_cards": catalog_cards
        })
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template catalog.html not found")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت محصولات: {e}")


def handle_product_new_get(headers):
    """Show add product form"""
    html = render_template("product_form.html", {"title": "افزودن محصول جدید"})
    if html:
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    return render_error_page(500, "Template product_form.html not found")


def handle_product_new_post(body, headers):
    """Process product addition"""
    form_data = parse_form_data(body)
    name = form_data.get('name', '').strip()
    description = form_data.get('description', '').strip()
    price = form_data.get('price', '0')
    category = form_data.get('category', '')
    is_active = form_data.get('is_active', '0')

    if not name:
        return render_error_page(400, "نام محصول الزامی است")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO products (name, description, price, category, is_active)
                       VALUES (?, ?, ?, ?, ?)
                       ''', (name, description, float(price) if price else 0, category, 1 if is_active == '1' else 0))
        conn.commit()
        conn.close()
        return '<p style="color:green">✅ Product added successfully!</p>', 200, {
            "Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return render_error_page(500, f"خطا در افزودن محصول: {e}")


def handle_products_list(headers):
    """Show products list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, description, price, category, is_active, created_at FROM products ORDER BY created_at DESC')
        products = cursor.fetchall()
        conn.close()

        table_rows = ""
        for p in products:
            status_class = "badge-success" if p['is_active'] else "badge-danger"
            status_text = "✅ Active" if p['is_active'] else "❌ Inactive"
            table_rows += f"""
            <tr>
                <td>{p['id']}</td>
                <td><strong>{p['name']}</strong></td>
                <td>{p['description'] or '-'}</td>
                <td>{p['price'] if p['price'] else '-'}</td>
                <td>{p['category'] or '-'}</td>
                <td><span class="badge {status_class}">{status_text}</span></td>
                <td>{p['created_at']}</td>
                <td>
                    <a href="/weather_platform/products/edit/{p['id']}" class="btn btn-sm btn-primary">✏️ ویرایش</a>
                    <a href="/weather_platform/products/view/{p['id']}" class="btn btn-sm btn-info">👁️ مشاهده</a>
                </td>
            </tr>
            """

        html = render_template("products_list.html", {"title": "لیست محصولات", "products_rows": table_rows})
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template products_list.html not found")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت محصولات: {e}")


def handle_product_edit_get(path, headers):
    """Show edit product form"""
    try:
        product_id = int(path.split("/")[-1])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, description, price, category, is_active FROM products WHERE id = ?',
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
            "price": product['price'] or 0,
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


def handle_product_edit_post(path, body, headers):
    """Process product edit"""
    try:
        product_id = int(path.split("/")[-1])
        form_data = parse_form_data(body)
        name = form_data.get('name', '').strip()
        description = form_data.get('description', '').strip()
        price = form_data.get('price', '0')
        category = form_data.get('category', '')
        is_active = form_data.get('is_active', '0')

        if not name:
            return render_error_page(400, "نام محصول الزامی است")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       UPDATE products
                       SET name        = ?,
                           description = ?,
                           price       = ?,
                           category    = ?,
                           is_active   = ?
                       WHERE id = ?
                       ''', (name, description, float(price) if price else 0, category, 1 if is_active == '1' else 0,
                             product_id))

        if cursor.rowcount == 0:
            conn.close()
            return render_error_page(404, f"محصول با شناسه {product_id} یافت نشد")

        conn.commit()
        conn.close()
        return '<p style="color:green">✅ Product updated successfully!</p>', 200, {
            "Content-Type": "text/html; charset=utf-8"}
    except ValueError:
        return render_error_page(400, "شناسه نامعتبر")
    except Exception as e:
        return render_error_page(500, f"خطا در بروزرسانی محصول: {e}")


def handle_product_view(path, headers):
    """View single product"""
    try:
        product_id = int(path.split("/")[-1])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT id, name, description, price, category, is_active, created_at FROM products WHERE id = ?',
            (product_id,))
        product = cursor.fetchone()

        # Get comments
        cursor.execute('''
                       SELECT c.id, c.comment, c.rating, c.created_at, u.username, u.full_name
                       FROM product_comments c
                                JOIN users u ON c.user_id = u.id
                       WHERE c.product_id = ?
                         AND c.is_approved = 1
                       ORDER BY c.created_at DESC
                       ''', (product_id,))
        comments = cursor.fetchall()
        conn.close()

        if not product:
            return render_error_page(404, f"محصول با شناسه {product_id} یافت نشد")

        status_text = "✅ فعال" if product['is_active'] else "❌ غیرفعال"
        price_display = f"{product['price']:,.0f}" if product['price'] else "رایگان"

        comments_html = ""
        for c in comments:
            stars = "⭐" * (c['rating'] or 0) + "☆" * (5 - (c['rating'] or 0))
            comments_html += f'''
            <div class="comment-item bg-gray-50 p-3 rounded-lg mb-2">
                <div class="flex items-center justify-between">
                    <span class="font-bold">{c['full_name'] or c['username']}</span>
                    <span class="text-sm text-gray-500">{c['created_at']}</span>
                </div>
                <div class="text-yellow-500">{stars}</div>
                <p class="text-gray-700 mt-1">{c['comment']}</p>
            </div>
            '''

        html = render_template("product_view.html", {
            "title": f"محصول: {product['name']}",
            "product_id": product_id,
            "name": product['name'],
            "description": product['description'] or 'توضیحی ثبت نشده',
            "price": price_display,
            "category": product['category'] or 'سایر',
            "is_active_text": status_text,
            "created_at": product['created_at'],
            "comments": comments_html or '<p class="text-gray-500">هنوز نظری ثبت نشده است</p>',
            "comments_count": len(comments)
        })
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template product_view.html not found")
    except ValueError:
        return render_error_page(404, "شناسه نامعتبر")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت محصول: {e}")