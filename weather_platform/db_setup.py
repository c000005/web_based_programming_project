import sqlite3

DATABASE_FILE = 'weather_platform.db'
dbc = sqlite3.connect(DATABASE_FILE)
cursor = dbc.cursor()

# ایجاد جداول
scriptSQL = '''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT DEFAULT 'guest',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_name TEXT NOT NULL,
        temperature REAL,
        humidity REAL,
        pressure REAL,
        wind_speed REAL,
        forecast_date TEXT,
        recorded_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
'''

cursor.executescript(scriptSQL)
dbc.commit()

print("تمامی جداول با موفقیت ایجاد شدند.")
dbc.close()