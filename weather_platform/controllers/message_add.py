# web_based_programming_project/weather_platform/controllers/message_add.py
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR / 'weather_platform.db'

def add_sample_message():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    message_data = (
        'رضا کریمی',                        # name
        'reza.karimi@example.com',          # email
        'درخواست همکاری',                   # subject
        'سلام، من تحلیل‌گر داده هواشناسی هستم و علاقه به همکاری دارم.',  # message
    )

    try:
        cursor.execute('''
            INSERT INTO messages (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        ''', message_data)
        conn.commit()
        print("[+] پیام جدید با موفقیت ذخیره شد.")
        print(f"    - از: {message_data[0]} <{message_data[1]}>")
        print(f"    - موضوع: {message_data[2]}")
    except Exception as e:
        print(f"[!] خطا در درج پیام: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_sample_message()