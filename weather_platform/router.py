# weather_platform/router.py

import importlib.util
from pathlib import Path

# Import controllers
from controllers import (
    auth_controller,
    weather_controller,
    product_controller,
    message_controller,
    user_controller,
    report_controller,
    cart_controller,
    wishlist_controller,
    comment_controller
)
from controllers.base_controller import render_error_page, render_template, json_response, get_db_connection


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

        # About page
        elif path == "/about":
            html = render_template("about.html", {"title": "درباره ما"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template about.html not found")

        # Dashboard
        elif path == "/dashboard":
            html = render_template("dashboard.html", {"title": "داشبورد مدیریت"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template dashboard.html not found")

        # ========== Auth Routes ==========
        elif path == "/register":
            return auth_controller.handle_register_get()

        # ========== Weather Routes ==========
        elif path == "/add_weather":
            return weather_controller.handle_add_weather_get()
        elif path == "/weather/list":
            return weather_controller.handle_weather_list()

        # ========== Product Routes ==========
        elif path == "/products/new":
            return product_controller.handle_product_new_get()
        elif path.startswith("/products/edit/"):
            return product_controller.handle_product_edit_get(path)
        elif path.startswith("/products/view/"):
            return product_controller.handle_product_view(path)
        elif path == "/products/list":
            return product_controller.handle_products_list()
        elif path == "/products/catalog":
            return product_controller.handle_products_catalog()

        # ========== Message Routes ==========
        elif path == "/messages/new":
            return message_controller.handle_message_form()
        elif path.startswith("/messages/view/"):
            return message_controller.handle_message_view(path)
        elif path == "/admin/messages":
            return message_controller.handle_messages_list()

        # ========== User Routes ==========
        elif path == "/users/new":
            return user_controller.handle_user_form()
        elif path.startswith("/admin/users/edit/"):
            return user_controller.handle_user_edit_get(path)
        elif path == "/admin/users":
            return user_controller.handle_users_list()

        # ========== Report Routes ==========
        elif path == "/reports/list":
            return report_controller.handle_reports_list()

        # ========== Cart Routes ==========
        elif path == "/cart":
            return cart_controller.handle_cart_view()
        elif path.startswith("/cart/add/"):
            return cart_controller.handle_cart_add(path)
        elif path.startswith("/cart/remove/"):
            return cart_controller.handle_cart_remove(path)

        # ========== Wishlist Routes ==========
        elif path == "/wishlist":
            return wishlist_controller.handle_wishlist_view()
        elif path.startswith("/wishlist/add/"):
            return wishlist_controller.handle_wishlist_add(path)
        elif path.startswith("/wishlist/remove/"):
            return wishlist_controller.handle_wishlist_remove(path)

        # ========== Comment Routes ==========
        # Note: Comments are handled within product view page

        # ========== API Routes ==========
        elif path == "/api/status":
            data = {"project": "weather_platform", "status": "ok"}
            return json_response(data)

        # 404
        else:
            return render_error_page(404, f"صفحه {path} یافت نشد")

    # POST request handling
    elif method == "POST":
        # ========== Auth Routes ==========
        if path == "/register":
            return auth_controller.handle_register_post(body)

        # ========== Weather Routes ==========
        elif path == "/add_weather":
            return weather_controller.handle_add_weather_post(body)

        # ========== Product Routes ==========
        elif path == "/products/new":
            return product_controller.handle_product_new_post(body)
        elif path.startswith("/products/edit/"):
            return product_controller.handle_product_edit_post(path, body)

        # ========== Message Routes ==========
        elif path == "/messages/new":
            return message_controller.handle_message_new_post(body)

        # ========== User Routes ==========
        elif path.startswith("/admin/users/edit/"):
            return user_controller.handle_user_edit_post(path, body)

        # ========== Cart Routes ==========
        elif path.startswith("/cart/add/"):
            return cart_controller.handle_cart_add(path)
        elif path.startswith("/cart/update/"):
            return cart_controller.handle_cart_update(path, body)
        elif path.startswith("/cart/remove/"):
            return cart_controller.handle_cart_remove(path)

        # ========== Wishlist Routes ==========
        elif path.startswith("/wishlist/add/"):
            return wishlist_controller.handle_wishlist_add(path)
        elif path.startswith("/wishlist/remove/"):
            return wishlist_controller.handle_wishlist_remove(path)

        # ========== Comment Routes ==========
        elif path.startswith("/products/comment/"):
            return comment_controller.handle_comment_add(path, body)

        # 404 for POST
        else:
            return render_error_page(404, f"صفحه {path} یافت نشد")

    # Method not allowed
    return render_error_page(405, "روش غیرمجاز")