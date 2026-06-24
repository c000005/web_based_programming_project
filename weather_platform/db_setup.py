# web_based_programming_project/weather_platform/db_setup.py
import sqlite3
import os
from pathlib import Path

DATABASE_FILE = 'weather_platform.db'
BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / DATABASE_FILE

def setup_database():
    """Create database with all tables if not exists"""
    if not os.path.exists(DATABASE_PATH):
        print(f"[*] Creating database: {DATABASE_FILE}")
        conn = sqlite3.connect(DATABASE_PATH)
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

        # 2. weather_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_code TEXT NOT NULL,
                city_name TEXT NOT NULL,
                country TEXT NOT NULL,
                record_date DATE NOT NULL,
                record_time TIME,
                temperature_celsius REAL,
                humidity_percent REAL,
                pressure_hpa REAL,
                wind_speed_ms REAL,
                wind_direction_deg INTEGER,
                precipitation_mm REAL,
                cloud_cover_percent REAL,
                visibility_km REAL,
                weather_condition TEXT,
                source TEXT DEFAULT 'synop',
                recorded_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recorded_by) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')

        # 3. analysis_reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                report_type TEXT,
                start_date DATE,
                end_date DATE,
                region TEXT,
                findings TEXT,
                chart_data TEXT,
                file_path TEXT,
                created_by INTEGER NOT NULL,
                is_public BOOLEAN DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')

        # 4. messages table
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

        # 5. saved_queries table
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

        # 6. products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                category TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
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

    else:
        print(f"[!] Database {DATABASE_FILE} already exists.")

if __name__ == '__main__':
    setup_database()