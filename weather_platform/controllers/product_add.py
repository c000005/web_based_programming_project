# web_based_programming_project/weather_platform/controllers/product_add.py
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
db_path = BASE_DIR / 'weather_platform.db'

def add_sample_product():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    product_data = (
        'گزارش فصلی تغییرات اقلیمی',         # name
        'تحلیل روند دما و بارش در ۱۰ سال اخیر',  # description
        299.99,                             # price (تومان یا هر واحد پولی)
        'custom_report',                    # category
        1,                                  # is_active
    )

    try:
        cursor.execute('''
            INSERT INTO products (name, description, price, category, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', product_data)
        conn.commit()
        print("[+] محصول/خدمت جدید با موفقیت اضافه شد.")
        print(f"    - نام: {product_data[0]}")
        print(f"    - قیمت: {product_data[2]}")
        print(f"    - دسته‌بندی: {product_data[3]}")
    except Exception as e:
        print(f"[!] خطا در درج محصول: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_sample_product()