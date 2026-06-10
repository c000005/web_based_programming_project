# web_based_programming_project/weather_platform/controllers/user_add.py
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR / 'weather_platform.db'

def add_sample_user():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # example information for an analyst user
    user_data = (
        'ahmad_meteo',                      # username
        'hashed_password_123',              # password_hash (در واقعیت باید hash کنی)
        'ahmad@weatherplatform.com',        # email
        'احمد محمدی',                       # full_name
        'analyst',                          # role
        1,                                  # is_active
    )

    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, full_name, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', user_data)
        conn.commit()
        print("[+] کاربر جدید با موفقیت اضافه شد.")
        print(f"    - username: {user_data[0]}")
        print(f"    - email: {user_data[2]}")
        print(f"    - role: {user_data[4]}")
    except sqlite3.IntegrityError as e:
        print(f"[!] خطا در درج کاربر: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_sample_user()