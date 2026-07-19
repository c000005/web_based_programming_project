# web_based_programming_project/weather_platform/controllers/cart_controller.py

from .base_controller import render_template, render_error_page, get_db_connection, parse_form_data
from core.permissions import has_permission, is_admin
from .auth_controller import get_current_user_from_headers


def get_user_id_from_headers(headers):
    """Get user ID from headers"""
    user = get_current_user_from_headers(headers)
    return user['id'] if user else None


def handle_cart_view(headers):
    """View shopping cart"""
    user_id = get_user_id_from_headers(headers)
    if not user_id:
        return render_error_page(401, "لطفاً برای مشاهده سبد خرید وارد شوید.")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT c.id as cart_id, c.quantity, c.added_at,
                              p.id as product_id, p.name as product_name,
                              p.description, p.price, p.category, p.is_active
                       FROM cart_items c
                       JOIN products p ON c.product_id = p.id
                       WHERE c.user_id = ?
                       ORDER BY c.added_at DESC
                       ''', (user_id,))

        cart_items = cursor.fetchall()
        conn.close()

        total_price = sum(item['price'] * item['quantity'] for item in cart_items if item['price'])

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


def handle_cart_add(path, headers):
    """Add item to cart"""
    user_id = get_user_id_from_headers(headers)
    if not user_id:
        return render_error_page(401, "لطفاً برای افزودن به سبد خرید وارد شوید.")

    try:
        product_id = int(path.split("/")[-1])

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

        cursor.execute('''
                       INSERT INTO cart_items (user_id, product_id, quantity)
                       VALUES (?, ?, 1) ON CONFLICT(user_id, product_id) 
                       DO UPDATE SET quantity = quantity + 1
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


def handle_cart_update(path, body, headers):
    """Update cart item quantity"""
    user_id = get_user_id_from_headers(headers)
    if not user_id:
        return render_error_page(401, "لطفاً برای بروزرسانی سبد خرید وارد شوید.")

    try:
        cart_id = int(path.split("/")[-1])
        form_data = parse_form_data(body)
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
                       WHERE id = ? AND user_id = ?
                       ''', (quantity, cart_id, user_id))

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


def handle_cart_remove(path, headers):
    """Remove item from cart"""
    user_id = get_user_id_from_headers(headers)
    if not user_id:
        return render_error_page(401, "لطفاً برای حذف از سبد خرید وارد شوید.")

    try:
        cart_id = int(path.split("/")[-1])

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cart_items WHERE id = ? AND user_id = ?', (cart_id, user_id))

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