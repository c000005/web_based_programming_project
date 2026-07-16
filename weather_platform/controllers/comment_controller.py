# web_based_programming_project/weather_platform/controllers/comment_controller.py

from .base_controller import render_error_page, get_db_connection, parse_form_data


def handle_comment_add(path, body):
    """Add comment for product"""
    try:
        product_id = int(path.split("/")[-1])
        user_id = 1  # Current active user
        form_data = parse_form_data(body)
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

        cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
        if not cursor.fetchone():
            conn.close()
            return render_error_page(404, "محصول مورد نظر یافت نشد")

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