# test_weather_platform_urllib.py
"""
Comprehensive test script for Weather Platform
Uses only Python standard library (no external dependencies)
"""

import os
import sys
import sqlite3
import json
import urllib.request
import urllib.error
import socket
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
PROJECT_PATH = "/weather_platform"


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name, status, details=""):
    """Print test result with color"""
    if status:
        print(f"{Colors.GREEN}✓ PASS{Colors.RESET}: {name}")
        if details:
            print(f"  {details}")
    else:
        print(f"{Colors.RED}✗ FAIL{Colors.RESET}: {name}")
        if details:
            print(f"  {Colors.RED}{details}{Colors.RESET}")


def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")


def url_request(url, timeout=5):
    """Make a request using urllib"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Test/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                'status': response.status,
                'content': response.read().decode('utf-8', errors='ignore'),
                'headers': dict(response.headers)
            }
    except urllib.error.HTTPError as e:
        return {'status': e.code, 'content': e.read().decode('utf-8', errors='ignore')}
    except urllib.error.URLError as e:
        return {'status': 0, 'error': str(e)}
    except socket.timeout:
        return {'status': 0, 'error': 'Timeout'}
    except Exception as e:
        return {'status': 0, 'error': str(e)}


def test_database_exists():
    """Test if database file exists"""
    db_path = Path(__file__).resolve().parent / "weather_platform" / "weather_platform.db"
    exists = db_path.exists()
    print_test("Database exists", exists, f"Path: {db_path}")
    return exists


def test_database_tables():
    """Test if all required tables exist"""
    db_path = Path(__file__).resolve().parent / "weather_platform" / "weather_platform.db"

    required_tables = [
        'users', 'sessions', 'weather_data', 'analysis_reports',
        'messages', 'saved_queries', 'products', 'cart_items',
        'wishlist_items', 'product_comments'
    ]

    if not db_path.exists():
        print_test("Database tables", False, "Database not found")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    missing = [t for t in required_tables if t not in tables]
    all_exist = len(missing) == 0

    print_test("All tables exist", all_exist,
               f"Found {len(tables)} tables, Missing: {missing if missing else 'None'}")
    return all_exist


def test_server_running():
    """Test if server is running"""
    result = url_request(f"{BASE_URL}/")
    is_running = result['status'] == 200
    print_test("Server is running", is_running, f"Status: {result['status']}")
    return is_running


def test_router_loaded():
    """Test if weather_platform router is loaded"""
    result = url_request(f"{BASE_URL}/")
    if result['status'] == 200:
        html = result['content']
        if "weather_platform" in html:
            print_test("Router loaded", True, "weather_platform found in index")
            return True
    print_test("Router loaded", False, "weather_platform not found")
    return False


def test_static_file():
    """Test static file serving"""
    result = url_request(f"{BASE_URL}{PROJECT_PATH}/static/css/style.css")
    is_ok = result['status'] == 200 and ".footer" in result['content']
    print_test("Static CSS served", is_ok,
               f"Status: {result['status']}, Size: {len(result['content'])} chars")
    return is_ok


def test_pages():
    """Test all main pages"""
    pages = [
        ("/", "Home page"),
        (f"{PROJECT_PATH}/", "Project home"),
        (f"{PROJECT_PATH}/login", "Login page"),
        (f"{PROJECT_PATH}/register", "Register page"),
        (f"{PROJECT_PATH}/dashboard", "Dashboard (requires auth)"),
        (f"{PROJECT_PATH}/about", "About page"),
        (f"{PROJECT_PATH}/contact", "Contact page"),
        (f"{PROJECT_PATH}/products/catalog", "Catalog page"),
        (f"{PROJECT_PATH}/weather/list", "Weather list"),
        (f"{PROJECT_PATH}/reports/list", "Reports list"),
        (f"{PROJECT_PATH}/admin/messages", "Messages list"),
        (f"{PROJECT_PATH}/admin/users", "Users list"),
        (f"{PROJECT_PATH}/cart", "Cart (requires auth)"),
        (f"{PROJECT_PATH}/wishlist", "Wishlist (requires auth)"),
    ]

    results = []
    for url, name in pages:
        try:
            full_url = f"{BASE_URL}{url}"
            result = url_request(full_url)
            is_ok = result['status'] in [200, 302, 401, 403]
            results.append(is_ok)
            print_test(f"Page: {name}", is_ok, f"Status: {result['status']}")
        except Exception as e:
            print_test(f"Page: {name}", False, str(e))
            results.append(False)

    return all(results)


def test_api_endpoint():
    """Test API status endpoint"""
    result = url_request(f"{BASE_URL}{PROJECT_PATH}/api/status")
    is_ok = result['status'] == 200
    if is_ok:
        try:
            data = json.loads(result['content'])
            is_ok = data.get('status') == 'ok'
            print_test("API endpoint /api/status", is_ok, f"Response: {result['content'][:100]}")
        except:
            print_test("API endpoint /api/status", False, "Invalid JSON response")
    else:
        print_test("API endpoint /api/status", False, f"Status: {result['status']}")
    return is_ok


def test_templates():
    """Test if templates exist"""
    template_dir = Path(__file__).resolve().parent / "weather_platform" / "templates"
    required_templates = [
        '_header.html', '_footer.html', '_nav.html',
        'index.html', 'login.html', 'register.html',
        'dashboard.html', 'about.html', 'error.html',
        'cart.html', 'wishlist.html', 'catalog.html',
        'products_list.html', 'product_edit.html', 'product_form.html',
        'product_view.html', 'users_list.html', 'user_edit.html',
        'messages_list.html', 'message_view.html', 'message_form.html',
        'weather_list.html', 'add_weather.html', 'reports_list.html',
        '403.html', '404.html'
    ]

    missing = []
    for template in required_templates:
        if not (template_dir / template).exists():
            missing.append(template)

    all_exist = len(missing) == 0
    print_test("All templates exist", all_exist,
               f"Found {len(required_templates) - len(missing)}/{len(required_templates)}, Missing: {missing[:3]}{'...' if len(missing) > 3 else ''}")
    return all_exist


def test_controllers():
    """Test if controllers exist"""
    controller_dir = Path(__file__).resolve().parent / "weather_platform" / "controllers"
    required_controllers = [
        '__init__.py', 'base_controller.py', 'auth_controller.py',
        'weather_controller.py', 'product_controller.py', 'message_controller.py',
        'user_controller.py', 'report_controller.py', 'cart_controller.py',
        'wishlist_controller.py', 'comment_controller.py'
    ]

    missing = []
    for controller in required_controllers:
        if not (controller_dir / controller).exists():
            missing.append(controller)

    all_exist = len(missing) == 0
    print_test("All controllers exist", all_exist,
               f"Missing: {missing if missing else 'None'}")
    return all_exist


def test_core_modules():
    """Test if core modules exist"""
    core_dir = Path(__file__).resolve().parent / "weather_platform" / "core"
    required_core = ['auth.py', 'cookie.py', 'permissions.py', 'response.py']

    missing = []
    for core in required_core:
        if not (core_dir / core).exists():
            missing.append(core)

    all_exist = len(missing) == 0
    print_test("All core modules exist", all_exist,
               f"Missing: {missing if missing else 'None'}")
    return all_exist


def test_setup_page():
    """Test database setup page"""
    result = url_request(f"{BASE_URL}{PROJECT_PATH}/setup", timeout=10)
    is_ok = result['status'] == 200 and "Database" in result['content']
    print_test("Database setup page", is_ok, f"Status: {result['status']}")
    return is_ok


def check_port(port):
    """Check if a port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0


def run_all_tests():
    """Run all tests and show summary"""
    print_section("🔧 WEATHER PLATFORM TEST SUITE")
    print(f"Testing against: {BASE_URL}")
    print(f"Project path: {PROJECT_PATH}")

    tests = [
        ("1. Database exists", test_database_exists),
        ("2. Database tables", test_database_tables),
        ("3. Server running", test_server_running),
        ("4. Router loaded", test_router_loaded),
        ("5. Static files", test_static_file),
        ("6. All pages", test_pages),
        ("7. API endpoint", test_api_endpoint),
        ("8. Templates", test_templates),
        ("9. Controllers", test_controllers),
        ("10. Core modules", test_core_modules),
        ("11. Setup page", test_setup_page),
    ]

    print_section("📋 TEST RESULTS")

    passed = 0
    total = len(tests)
    results = []

    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            if result:
                passed += 1
        except Exception as e:
            print_test(name, False, f"Error: {str(e)}")
            results.append((name, False))

    print_section("📊 SUMMARY")
    print(f"Total tests: {total}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.RESET}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.RESET}")
    print(f"Success rate: {Colors.BOLD}{(passed / total) * 100:.1f}%{Colors.RESET}")

    # Show failed tests
    if passed < total:
        print_section("❌ FAILED TESTS")
        for name, result in results:
            if not result:
                print(f"  {Colors.RED}✗ {name}{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Your project is ready!{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠️ Some tests failed. Check the output above for details.{Colors.RESET}")


if __name__ == "__main__":
    if not check_port(8000):
        print(f"{Colors.YELLOW}Warning: Server doesn't seem to be running on port 8000{Colors.RESET}")
        print("Please start the server first:")
        print("  cd C:\\Users\\ma\\Documents\\GitHub\\web_based_programming_project")
        print("  python web_server.py")
        print()
        response = input("Continue with tests anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)

    run_all_tests()