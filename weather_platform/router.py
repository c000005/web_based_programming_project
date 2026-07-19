# web_based_programming_project/weather_platform/router.py

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


def route(path, method, body, headers):
    """Main routing function using match case"""

    match method:
        case "GET":
            return handle_get_requests(path, headers)
        case "POST":
            return handle_post_requests(path, body, headers)
        case _:
            return render_error_page(405, "روش غیرمجاز")


def handle_get_requests(path, headers):
    """Handle all GET requests using match case"""

    # ========== Auth Routes ==========
    match path:
        case "/login":
            return auth_controller.handle_login_get()
        case "/logout":
            return auth_controller.handle_logout(headers)

        # Setup route
        case "/setup":
            result = run_db_setup()
            return f"<p>{result}</p>", 200, {"Content-Type": "text/html; charset=utf-8"}

        # Static pages
        case "/":
            html = render_template("index.html", {"title": "پلتفرم هواشناسی"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template index.html not found")

        case "/contact":
            html = render_template("message_form.html", {"title": "تماس با ما"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template message_form.html not found")

        case "/about":
            html = render_template("about.html", {"title": "درباره ما"})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template about.html not found")

        case "/dashboard":
            # Check authentication
            current_user = auth_controller.get_current_user_from_headers(headers)
            if not current_user:
                html = render_template("login.html", {
                    "title": "ورود به سیستم",
                    "error": "لطفاً برای دسترسی به داشبورد وارد شوید."
                })
                return html, 401, {"Content-Type": "text/html; charset=utf-8"}
            html = render_template("dashboard.html", {"title": "داشبورد مدیریت", "user": current_user})
            if html:
                return html, 200, {"Content-Type": "text/html; charset=utf-8"}
            return render_error_page(500, "Template dashboard.html not found")

        # ========== Register Route ==========
        case "/register":
            return auth_controller.handle_login_get()  # Or keep register form separately

        # ========== Weather Routes ==========
        case "/add_weather":
            return weather_controller.handle_add_weather_get(headers)
        case "/weather/list":
            return weather_controller.handle_weather_list(headers)

        # ========== Product Routes ==========
        case "/products/new":
            return product_controller.handle_product_new_get(headers)
        case "/products/list":
            return product_controller.handle_products_list(headers)
        case "/products/catalog":
            return product_controller.handle_products_catalog(headers)

        # ========== Message Routes ==========
        case "/messages/new":
            return message_controller.handle_message_form(headers)
        case "/admin/messages":
            return message_controller.handle_messages_list(headers)

        # ========== User Routes ==========
        case "/users/new":
            return user_controller.handle_user_form(headers)
        case "/admin/users":
            return user_controller.handle_users_list(headers)

        # ========== Report Routes ==========
        case "/reports/list":
            return report_controller.handle_reports_list(headers)

        # ========== Cart Routes ==========
        case "/cart":
            return cart_controller.handle_cart_view(headers)

        # ========== Wishlist Routes ==========
        case "/wishlist":
            return wishlist_controller.handle_wishlist_view(headers)

        # ========== API Routes ==========
        case "/api/status":
            data = {"project": "weather_platform", "status": "ok"}
            return json_response(data)

        # ========== Dynamic Routes with Path Parameters ==========
        # Product dynamic routes
        case path if path.startswith("/products/edit/"):
            return product_controller.handle_product_edit_get(path, headers)
        case path if path.startswith("/products/view/"):
            return product_controller.handle_product_view(path, headers)

        # Message dynamic routes
        case path if path.startswith("/messages/view/"):
            return message_controller.handle_message_view(path, headers)

        # User dynamic routes
        case path if path.startswith("/admin/users/edit/"):
            return user_controller.handle_user_edit_get(path, headers)

        # Cart dynamic routes (GET for add/remove)
        case path if path.startswith("/cart/add/"):
            return cart_controller.handle_cart_add(path, headers)
        case path if path.startswith("/cart/remove/"):
            return cart_controller.handle_cart_remove(path, headers)

        # Wishlist dynamic routes (GET for add/remove)
        case path if path.startswith("/wishlist/add/"):
            return wishlist_controller.handle_wishlist_add(path, headers)
        case path if path.startswith("/wishlist/remove/"):
            return wishlist_controller.handle_wishlist_remove(path, headers)

        # 404 - Page not found
        case _:
            return render_error_page(404, f"صفحه {path} یافت نشد")


def handle_post_requests(path, body, headers):
    """Handle all POST requests using match case"""

    match path:
        # ========== Auth Routes ==========
        case "/login":
            return auth_controller.handle_login_post(body)
        case "/register":
            return auth_controller.handle_register_post(body)

        # ========== Weather Routes ==========
        case "/add_weather":
            return weather_controller.handle_add_weather_post(body, headers)

        # ========== Product Routes ==========
        case "/products/new":
            return product_controller.handle_product_new_post(body, headers)

        # ========== Message Routes ==========
        case "/messages/new":
            return message_controller.handle_message_new_post(body, headers)

        # ========== Product Dynamic Routes ==========
        case path if path.startswith("/products/edit/"):
            return product_controller.handle_product_edit_post(path, body, headers)

        # ========== User Dynamic Routes ==========
        case path if path.startswith("/admin/users/edit/"):
            return user_controller.handle_user_edit_post(path, body, headers)

        # ========== Cart Dynamic Routes ==========
        case path if path.startswith("/cart/add/"):
            return cart_controller.handle_cart_add(path, headers)
        case path if path.startswith("/cart/update/"):
            return cart_controller.handle_cart_update(path, body, headers)
        case path if path.startswith("/cart/remove/"):
            return cart_controller.handle_cart_remove(path, headers)

        # ========== Wishlist Dynamic Routes ==========
        case path if path.startswith("/wishlist/add/"):
            return wishlist_controller.handle_wishlist_add(path, headers)
        case path if path.startswith("/wishlist/remove/"):
            return wishlist_controller.handle_wishlist_remove(path, headers)

        # ========== Comment Routes ==========
        case path if path.startswith("/products/comment/"):
            return comment_controller.handle_comment_add(path, body, headers)

        # 404 for POST
        case _:
            return render_error_page(404, f"صفحه {path} یافت نشد")