# web_based_programming_project/weather_platform/controllers/product_controller.py

from .base_controller import render_template, render_error_page, get_db_connection, parse_form_data


def handle_product_new_get():
    """Show add product form"""
    html = render_template("product_form.html", {"title": "افزودن محصول جدید"})
    if html:
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    return render_error_page(500, "Template product_form.html not found")


def handle_product_new_post(body):
    """Process product addition"""
    form_data = parse_form_data(body)
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


def handle_product_edit_get(path):
    """Show edit product form"""
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


def handle_product_edit_post(path, body):
    """Process product edit"""
    try:
        product_id = int(path.split("/")[-1])
        form_data = parse_form_data(body)
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


def handle_product_view(path):
    """View single product with comments"""
    try:
        product_id = int(path.split("/")[-1])
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id, name, description, price, category, is_active, created_at FROM products WHERE id = ?',
            (product_id,))
        product = cursor.fetchone()

        if not product:
            conn.close()
            return render_error_page(404, f"محصول با شناسه {product_id} یافت نشد")

        # Get comments with user info
        cursor.execute('''
                       SELECT c.id as comment_id, c.comment, c.rating, c.created_at,
                              u.id as user_id, u.username, u.full_name
                       FROM product_comments c
                       JOIN users u ON c.user_id = u.id
                       WHERE c.product_id = ? AND c.is_approved = 1
                       ORDER BY c.created_at DESC
                       ''', (product_id,))

        comments = cursor.fetchall()
        conn.close()

        # Build comments HTML
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


def handle_products_list():
    """Show products list"""
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


def handle_products_catalog():
    """Show products catalog"""
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