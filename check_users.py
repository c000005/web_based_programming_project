# check_users.py
import sqlite3
from pathlib import Path

db_path = Path("weather_platform/weather_platform.db")

if not db_path.exists():
    print("❌ Database not found!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check users table
    cursor.execute("SELECT id, username, password_hash, email, role FROM users")
    users = cursor.fetchall()

    print("📋 Users in database:")
    print("-" * 50)
    if users:
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Password: {user[2]}, Role: {user[4]}")
    else:
        print("No users found!")

    conn.close()