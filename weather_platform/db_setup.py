# web_based_programming_project/weather_platform/db_setup.py
import sqlite3
import os
from pathlib import Path

DATABASE_FILE = 'weather_platform.db'
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / DATABASE_FILE

def setup_database():
    # چک کردن وجود فایل دیتابیس
    if not os.path.exists(DATABASE_PATH):
        print(f"[*] ساخت دیتابیس: {DATABASE_FILE}")
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # 1. جدول users (کاربران سیستم - تحلیل‌گران و ادمین‌ها)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'analyst',   -- 'admin', 'analyst', 'viewer'
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')

        # 2. جدول weather_data (داده‌های خام هواشناسی)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_code TEXT NOT NULL,
                city_name TEXT NOT NULL,
                country TEXT NOT NULL,
                record_date DATE NOT NULL,
                record_time TIME,
                temperature_celsius REAL,        -- دمای سلسیوس
                humidity_percent REAL,           -- رطوبت درصدی
                pressure_hpa REAL,               -- فشار هوا (هکتوپاسکال)
                wind_speed_ms REAL,              -- سرعت باد (متر بر ثانیه)
                wind_direction_deg INTEGER,      -- جهت باد (درجه)
                precipitation_mm REAL,           -- بارندگی (میلی‌متر)
                cloud_cover_percent REAL,        -- پوشش ابر (درصد)
                visibility_km REAL,              -- دید (کیلومتر)
                weather_condition TEXT,          -- وضعیت هوا (بارانی، آفتابی و...)
                source TEXT DEFAULT 'synop',     -- منبع داده
                recorded_by INTEGER,             -- کاربر ثبت‌کننده (ارجاع به users.id)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recorded_by) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')

        # 3. جدول analysis_reports (گزارش‌های تحلیلی تولید شده توسط تحلیل‌گران)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                report_type TEXT,                -- 'forecast', 'trend', 'extreme_weather', 'climate_change'
                start_date DATE,
                end_date DATE,
                region TEXT,                     -- منطقه تحت تحلیل
                findings TEXT,                   -- یافته‌های کلیدی (JSON یا متن)
                chart_data TEXT,                 -- داده‌های نمودار (JSON)
                file_path TEXT,                  -- مسیر فایل گزارش (PDF/HTML)
                created_by INTEGER NOT NULL,     -- تحلیل‌گر ایجادکننده
                is_public BOOLEAN DEFAULT 0,     -- عمومی یا خصوصی
                view_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # 4. جدول messages (فرم تماس - طبق خواسته استاد)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                replied_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 5. جدول optional: saved_queries (ذخیره کوئری‌های تحلیلی پرکاربرد توسط تحلیل‌گران)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_name TEXT NOT NULL,
                sql_query TEXT NOT NULL,
                description TEXT,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # 6. جدول products (جدید طبق تمرین استاد)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                category TEXT,      -- مثلا 'subscription', 'api_access', 'custom_report'
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # commit و بستن اتصال
        conn.commit()
        conn.close()

        print("[+] دیتابیس و تمام جداول با موفقیت ساخته شد.")
        print("    - users")
        print("    - weather_data")
        print("    - analysis_reports")
        print("    - messages")
        print("    - saved_queries")

    else:
        print(f"[!] دیتابیس {DATABASE_FILE} از قبل وجود دارد.")

if __name__ == '__main__':
    setup_database()