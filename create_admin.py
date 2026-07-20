# create_admin.py
import sqlite3
from pathlib import Path

db_path = Path("weather_platform/weather_platform.db")

if not db_path.exists():
    print("❌ Database not found!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if admin exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    existing = cursor.fetchone()

    if existing:
        print(f"✅ Admin user already exists with ID: {existing[0]}")
    else:
        # Create admin user
        cursor.execute('''
                       INSERT INTO users (username, password_hash, email, full_name, role, is_active)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', ('admin', 'admin123', 'admin@weather.com', 'مدیر سیستم', 'admin', 1))

        conn.commit()
        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Password: admin123")

    # Show all users
    cursor.execute("SELECT id, username, password_hash, role FROM users")
    users = cursor.fetchall()
    print("\n📋 All users:")
    for user in users:
        print(f"  {user[0]}: {user[1]} (role: {user[3]})")

    conn.close()