# web_based_programming_project/weather_platform/db_setup.py

import sqlite3
import os
from pathlib import Path
import settings


def setup_database():
    """Create database with all tables if not exists"""
    if not os.path.exists(settings.DB_PATH):
        print(f"[*] Creating database: {settings.DB_NAME}")
        conn = sqlite3.connect(settings.DB_PATH)
        cursor = conn.cursor()

        # 1. users table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           username TEXT UNIQUE NOT NULL,
                           password_hash TEXT NOT NULL,
                           email TEXT UNIQUE NOT NULL,
                           full_name TEXT,
                           role TEXT DEFAULT 'viewer',
                           is_active BOOLEAN DEFAULT 1,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           last_login TIMESTAMP
                       )
                       ''')

        # 2. Sessions table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS sessions
                       (
                           id
                           TEXT
                           PRIMARY
                           KEY,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           expires_at
                           TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       )
                           )
                       ''')

        # 2. weather_data table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS weather_data
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           station_code
                           TEXT
                           NOT
                           NULL,
                           city_name
                           TEXT
                           NOT
                           NULL,
                           country
                           TEXT
                           NOT
                           NULL,
                           record_date
                           DATE
                           NOT
                           NULL,
                           record_time
                           TIME,
                           temperature_celsius
                           REAL,
                           humidity_percent
                           REAL,
                           pressure_hpa
                           REAL,
                           wind_speed_ms
                           REAL,
                           wind_direction_deg
                           INTEGER,
                           precipitation_mm
                           REAL,
                           cloud_cover_percent
                           REAL,
                           visibility_km
                           REAL,
                           weather_condition
                           TEXT,
                           source
                           TEXT
                           DEFAULT
                           'synop',
                           recorded_by
                           INTEGER,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           recorded_by
                       ) REFERENCES users
                       (
                           id
                       ) ON DELETE SET NULL
                           )
                       ''')

        # 3. analysis_reports table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS analysis_reports
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           title
                           TEXT
                           NOT
                           NULL,
                           description
                           TEXT,
                           report_type
                           TEXT,
                           start_date
                           DATE,
                           end_date
                           DATE,
                           region
                           TEXT,
                           findings
                           TEXT,
                           chart_data
                           TEXT,
                           file_path
                           TEXT,
                           created_by
                           INTEGER
                           NOT
                           NULL,
                           is_public
                           BOOLEAN
                           DEFAULT
                           0,
                           view_count
                           INTEGER
                           DEFAULT
                           0,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           updated_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           created_by
                       ) REFERENCES users
                       (
                           id
                       ) ON DELETE CASCADE
                           )
                       ''')

        # 4. messages table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS messages
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT
                           NOT
                           NULL,
                           email
                           TEXT
                           NOT
                           NULL,
                           subject
                           TEXT,
                           message
                           TEXT
                           NOT
                           NULL,
                           is_read
                           BOOLEAN
                           DEFAULT
                           0,
                           replied_at
                           TIMESTAMP,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # 5. saved_queries table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS saved_queries
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           query_name
                           TEXT
                           NOT
                           NULL,
                           sql_query
                           TEXT
                           NOT
                           NULL,
                           description
                           TEXT,
                           created_by
                           INTEGER
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           created_by
                       ) REFERENCES users
                       (
                           id
                       ) ON DELETE CASCADE
                           )
                       ''')

        # 6. products table
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS products
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           name
                           TEXT
                           NOT
                           NULL,
                           description
                           TEXT,
                           price
                           REAL,
                           category
                           TEXT,
                           is_active
                           BOOLEAN
                           DEFAULT
                           1,
                           is_deleted
                           BOOLEAN
                           DEFAULT
                           0,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # ========== جداول جدید برای سبد خرید، علاقمندی‌ها و نظرات ==========

        # 7. cart_items table (سبد خرید)
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS cart_items
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           product_id
                           INTEGER
                           NOT
                           NULL,
                           quantity
                           INTEGER
                           DEFAULT
                           1,
                           added_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       ) ON DELETE CASCADE,
                           FOREIGN KEY
                       (
                           product_id
                       ) REFERENCES products
                       (
                           id
                       )
                         ON DELETE CASCADE,
                           UNIQUE
                       (
                           user_id,
                           product_id
                       )
                           )
                       ''')

        # 8. wishlist_items table (علاقمندی‌ها)
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS wishlist_items
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           product_id
                           INTEGER
                           NOT
                           NULL,
                           added_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       ) ON DELETE CASCADE,
                           FOREIGN KEY
                       (
                           product_id
                       ) REFERENCES products
                       (
                           id
                       )
                         ON DELETE CASCADE,
                           UNIQUE
                       (
                           user_id,
                           product_id
                       )
                           )
                       ''')

        # 9. product_comments table (نظرات محصولات)
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS product_comments
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           product_id
                           INTEGER
                           NOT
                           NULL,
                           user_id
                           INTEGER
                           NOT
                           NULL,
                           comment
                           TEXT
                           NOT
                           NULL,
                           rating
                           INTEGER
                           CHECK
                       (
                           rating
                           >=
                           1
                           AND
                           rating
                           <=
                           5
                       ),
                           is_approved BOOLEAN DEFAULT 1,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                           FOREIGN KEY
                       (
                           product_id
                       ) REFERENCES products
                       (
                           id
                       ) ON DELETE CASCADE,
                           FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           id
                       )
                         ON DELETE CASCADE
                           )
                       ''')

        # ========== اضافه کردن داده‌های اولیه ==========

        # اضافه کردن کاربر پیش‌فرض (با شناسه 1)
        cursor.execute('''
                       INSERT
                       OR IGNORE INTO users (id, username, password_hash, email, full_name, role, is_active)
            VALUES (1, 'admin', 'admin123', 'admin@weather.com', 'مدیر سیستم', 'admin', 1)
                       ''')

        # اضافه کردن محصولات نمونه (اگر قبلاً اضافه نشده باشند)
        cursor.execute('''
                       INSERT
                       OR IGNORE INTO products (id, name, description, price, category, is_active)
            VALUES 
                (1, 'اشتراک حرفه‌ای هواشناسی', 'دسترسی کامل به داده‌های هواشناسی و گزارش‌های تحلیلی', 990000, 'subscription', 1),
                (2, 'دسترسی API پیشرفته', 'دسترسی به API با 10000 درخواست روزانه', 1490000, 'api_access', 1),
                (3, 'گزارش سفارشی فصلی', 'گزارش تحلیلی سفارشی برای هر فصل', 2500000, 'custom_report', 1),
                (4, 'داده‌های لحظه‌ای هواشناسی', 'دسترسی به داده‌های لحظه‌ای 50 شهر ایران', 790000, 'subscription', 1)
                       ''')

        conn.commit()
        conn.close()

        print("[+] Database and all tables created successfully.")
        print("    - users")
        print("    - weather_data")
        print("    - analysis_reports")
        print("    - messages")
        print("    - saved_queries")
        print("    - products")
        print("    - cart_items (NEW)")  # جدید
        print("    - wishlist_items (NEW)")  # جدید
        print("    - product_comments (NEW)")  # جدید

    else:
        print(f"[!] Database {settings.DB_NAME} already exists.")

        # امکان اضافه کردن جداول جدید به دیتابیس موجود
        print("[*] Checking for new tables...")
        conn = sqlite3.connect(settings.DB_PATH)
        cursor = conn.cursor()

        # بررسی و اضافه کردن جدول cart_items اگر وجود ندارد
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cart_items'")
        if not cursor.fetchone():
            print("[*] Adding cart_items table...")
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS cart_items
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               user_id
                               INTEGER
                               NOT
                               NULL,
                               product_id
                               INTEGER
                               NOT
                               NULL,
                               quantity
                               INTEGER
                               DEFAULT
                               1,
                               added_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               user_id
                           ) REFERENCES users
                           (
                               id
                           ) ON DELETE CASCADE,
                               FOREIGN KEY
                           (
                               product_id
                           ) REFERENCES products
                           (
                               id
                           )
                             ON DELETE CASCADE,
                               UNIQUE
                           (
                               user_id,
                               product_id
                           )
                               )
                           ''')
            print("    ✓ cart_items table added")

        # بررسی و اضافه کردن جدول wishlist_items اگر وجود ندارد
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wishlist_items'")
        if not cursor.fetchone():
            print("[*] Adding wishlist_items table...")
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS wishlist_items
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               user_id
                               INTEGER
                               NOT
                               NULL,
                               product_id
                               INTEGER
                               NOT
                               NULL,
                               added_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               user_id
                           ) REFERENCES users
                           (
                               id
                           ) ON DELETE CASCADE,
                               FOREIGN KEY
                           (
                               product_id
                           ) REFERENCES products
                           (
                               id
                           )
                             ON DELETE CASCADE,
                               UNIQUE
                           (
                               user_id,
                               product_id
                           )
                               )
                           ''')
            print("    ✓ wishlist_items table added")

        # بررسی و اضافه کردن جدول product_comments اگر وجود ندارد
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='product_comments'")
        if not cursor.fetchone():
            print("[*] Adding product_comments table...")
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS product_comments
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               product_id
                               INTEGER
                               NOT
                               NULL,
                               user_id
                               INTEGER
                               NOT
                               NULL,
                               comment
                               TEXT
                               NOT
                               NULL,
                               rating
                               INTEGER
                               CHECK
                           (
                               rating
                               >=
                               1
                               AND
                               rating
                               <=
                               5
                           ),
                               is_approved BOOLEAN DEFAULT 1,
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               FOREIGN KEY
                           (
                               product_id
                           ) REFERENCES products
                           (
                               id
                           ) ON DELETE CASCADE,
                               FOREIGN KEY
                           (
                               user_id
                           ) REFERENCES users
                           (
                               id
                           )
                             ON DELETE CASCADE
                               )
                           ''')
            print("    ✓ product_comments table added")

        conn.commit()
        conn.close()
        print("[+] Database update completed.")

        add_is_deleted_column()


def add_is_deleted_column():
    """Add is_deleted column to products table if not exists"""
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute("PRAGMA table_info(products)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'is_deleted' not in columns:
        print("[*] Adding is_deleted column to products table...")
        cursor.execute('ALTER TABLE products ADD COLUMN is_deleted BOOLEAN DEFAULT 0')
        print("    ✓ is_deleted column added")

    conn.commit()
    conn.close()


if __name__ == '__main__':
    setup_database()