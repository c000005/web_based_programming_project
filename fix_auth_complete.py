# fix_auth_complete.py
"""
Complete fix for authentication
"""
import os
import sqlite3
from pathlib import Path


def fix_database():
    """Ensure admin user exists"""
    print("🔧 Checking database...")
    db_path = Path("weather_platform/weather_platform.db")

    if not db_path.exists():
        print("❌ Database not found! Run python weather_platform/db_setup.py first")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if admin exists
    cursor.execute("SELECT id, username, password_hash FROM users WHERE username = 'admin'")
    admin = cursor.fetchone()

    if admin:
        print(f"✅ Admin user found: ID={admin[0]}, Password='{admin[2]}'")
        # Update password to ensure it matches
        cursor.execute("UPDATE users SET password_hash = 'admin123' WHERE username = 'admin'")
        conn.commit()
        print("✅ Admin password reset to 'admin123'")
    else:
        # Create admin user
        cursor.execute('''
                       INSERT INTO users (username, password_hash, email, full_name, role, is_active)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', ('admin', 'admin123', 'admin@weather.com', 'مدیر سیستم', 'admin', 1))
        conn.commit()
        print("✅ Admin user created with password 'admin123'")

    # Show all users
    cursor.execute("SELECT id, username, password_hash, role FROM users")
    users = cursor.fetchall()
    print("\n📋 Users in database:")
    for user in users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Password: '{user[2]}', Role: {user[3]}")

    conn.close()
    return True


def fix_auth_controller():
    """Update auth_controller with better error messages"""
    print("\n🔧 Updating auth_controller.py...")
    file_path = Path("weather_platform/controllers/auth_controller.py")

    if not file_path.exists():
        print("❌ auth_controller.py not found")
        return False

    content = file_path.read_text(encoding="utf-8")

    # Update the error message to be more specific
    content = content.replace(
        '"نام کاربری یا رمز عبور اشتباه است."',
        '"نام کاربری یا رمز عبور اشتباه است. لطفاً دوباره تلاش کنید."'
    )

    file_path.write_text(content, encoding="utf-8")
    print("✅ Updated auth_controller.py")
    return True


def run():
    print("=" * 60)
    print("🔧 AUTHENTICATION FIX TOOL")
    print("=" * 60)

    fix_database()
    fix_auth_controller()

    print("\n" + "=" * 60)
    print("✅ Fixes applied!")
    print("\n📝 Login with:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n   Then visit: http://localhost:8000/weather_platform/dashboard")
    print("=" * 60)


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    run()