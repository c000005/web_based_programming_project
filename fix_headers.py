# fix_headers.py
"""
Fix all controller functions to accept headers parameter
"""

import os
import re
from pathlib import Path


def fix_controller(file_path, functions):
    """Fix a controller file by adding headers=None to functions"""
    if not file_path.exists():
        print(f"❌ {file_path} not found")
        return False

    content = file_path.read_text(encoding="utf-8")
    modified = False

    for func_name in functions:
        # Find function definition
        pattern = rf'def {func_name}\(([^)]*)\):'
        match = re.search(pattern, content)
        if match:
            params = match.group(1).strip()
            if 'headers' not in params:
                if params:
                    new_params = f"{params}, headers=None"
                else:
                    new_params = "headers=None"
                old_def = f"def {func_name}({params}):"
                new_def = f"def {func_name}({new_params}):"
                content = content.replace(old_def, new_def)
                modified = True
                print(f"  ✅ Fixed {func_name}")

    if modified:
        file_path.write_text(content, encoding="utf-8")
        return True
    return False


def run():
    print("=" * 60)
    print("🔧 FIXING CONTROLLER HEADER PARAMETERS")
    print("=" * 60)

    base_dir = Path("weather_platform/controllers")

    fixes = [
        ("weather_controller.py", ["handle_add_weather_get", "handle_add_weather_post", "handle_weather_list"]),
        ("report_controller.py", ["handle_reports_list"]),
        ("message_controller.py",
         ["handle_message_form", "handle_message_new_post", "handle_messages_list", "handle_message_view"]),
        ("user_controller.py",
         ["handle_user_form", "handle_user_edit_get", "handle_user_edit_post", "handle_users_list"]),
        ("product_controller.py",
         ["handle_products_catalog", "handle_product_new_get", "handle_product_new_post", "handle_products_list",
          "handle_product_edit_get", "handle_product_edit_post", "handle_product_view"]),
        ("cart_controller.py", ["handle_cart_view", "handle_cart_add", "handle_cart_update", "handle_cart_remove"]),
        ("wishlist_controller.py", ["handle_wishlist_view", "handle_wishlist_add", "handle_wishlist_remove"]),
        ("comment_controller.py", ["handle_comment_add"]),
    ]

    for filename, functions in fixes:
        file_path = base_dir / filename
        print(f"\n📝 Fixing {filename}...")
        fix_controller(file_path, functions)

    print("\n" + "=" * 60)
    print("✅ All controllers fixed!")
    print("\n📝 Restart the server:")
    print("   python web_server.py")
    print("=" * 60)


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    run()