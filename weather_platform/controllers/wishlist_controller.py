# web_based_programming_project/weather_platform/controllers/wishlist_controller.py

from .base_controller import render_template, render_error_page, get_db_connection


def handle_wishlist_view():
    """View wishlist"""
    try:
        user_id = 1  # Current active user
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT w.id as wish_id, w.added_at,
                              p.id as product_id, p.name as product_name,
                              p.description, p.price, p.category, p.is_active
                       FROM wishlist_items w
                       JOIN products p ON w.product_id = p.id
                       WHERE w.user_id = ?
                       ORDER BY w.added_at DESC
                       ''', (user_id,))

        wishlist_items = cursor.fetchall()
        conn.close()

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


def handle_wishlist_add(path):
    """Add item to wishlist"""
    try:
        product_id = int(path.split("/")[-1])
        user_id = 1

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
        product = cursor.fetchone()

        if not product:
            conn.close()
            return render_error_page(404, "محصول مورد نظر یافت نشد")

        cursor.execute('''
                       INSERT OR IGNORE INTO wishlist_items (user_id, product_id)
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


def handle_wishlist_remove(path):
    """Remove item from wishlist"""
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