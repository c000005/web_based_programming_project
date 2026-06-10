# web_based_programming_project/weather_platform/controllers/add_message.py

import sqlite3

from pathlib import Path

#import importlib.util use if needed

DATABASE_FILE = '../weather_platform.db'

BASE_DIR = Path(__file__).resolve().parent

# مسیر دیتابیس در داخل پوشه پروژه

DATABASE_PATH = BASE_DIR / DATABASE_FILE

def handle():

    # 1. connect DB

    dbc = sqlite3.connect( DATABASE_PATH )

    cursor = dbc.cursor()

    # 2. execute SQL script

    message = ('reza razavi', 'reza@yahoo.com', 'سایت خالی به چه درد می خوره؟') # tupple

    script_sql = '''

                INSERT INTO messages(name, email, message)

                VALUES(?, ?, ?)

            '''

    cursor.execute(script_sql, message)

    dbc.commit()

    print('پیام با موفقیت درج شد')

    # 3. close connection

    dbc.close()