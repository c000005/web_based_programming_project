import json
import sqlite3
from pathlib import Path

DATABASE_FILE = Path(__file__).resolve().parent / "weather_platform.db"


def render_template(filename):
    base_dir = Path(__file__).resolve().parent
    template_path = base_dir / "templates" / filename
    if not template_path.exists():
        return None
    return template_path.read_text(encoding="utf-8")


def save_message(name, email, message):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                   (name, email, message))
    conn.commit()
    conn.close()


def register_user(username, password, email, role):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)",
                       (username, password, email, role))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def save_weather_data(station_name, temperature, humidity, pressure, wind_speed, forecast_date, recorded_by):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO weather_data (station_name, temperature, humidity, pressure, wind_speed, forecast_date,
                                             recorded_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ''', (station_name, temperature, humidity, pressure, wind_speed, forecast_date, recorded_by))
    conn.commit()
    conn.close()


def route(path, method, body):
    # ------------------- صفحه اصلی -------------------
    if path == "/":
        html = render_template("index.html")
        if html:
            return (html, 200, {"Content-Type": "text/html; charset=utf-8"})
        return ("Template index.html not found", 500, {"Content-Type": "text/plain"})

    # ------------------- فرم تماس -------------------
    if path == "/contact":
        if method == "POST" and body:
            # تجزیه داده‌های فرم
            import urllib.parse
            data = urllib.parse.parse_qs(body)
            name = data.get('name', [''])[0]
            email = data.get('email', [''])[0]
            message = data.get('message', [''])[0]
            if name and email and message:
                save_message(name, email, message)
                # نمایش موفقیت
                html = render_template("contact.html")
                html = html.replace(
                    "{% if success %}<p class='success'>✅ پیام شما با موفقیت ارسال شد.</p>{% elif error %}{% endif %}",
                    "<p class='success'>✅ پیام شما با موفقیت ارسال شد.</p>")
                html = html.replace("{% if success %}", "").replace("{% elif error %}", "").replace("{% endif %}", "")
                return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

        html = render_template("contact.html")
        html = html.replace("{% if success %}", "").replace("{% elif error %}", "").replace("{% endif %}", "")
        return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

    # ------------------- فرم ثبت‌نام -------------------
    if path == "/register":
        if method == "POST" and body:
            import urllib.parse
            data = urllib.parse.parse_qs(body)
            username = data.get('username', [''])[0]
            password = data.get('password', [''])[0]
            email = data.get('email', [''])[0]
            role = data.get('role', ['guest'])[0]

            if register_user(username, password, email, role):
                html = render_template("register.html")
                html = html.replace(
                    "{% if success %}<p class='success'>✅ ثبت‌نام موفق! اکنون می‌توانید وارد شوید.</p>{% elif error %}{% endif %}",
                    "<p class='success'>✅ ثبت‌نام موفق! اکنون می‌توانید وارد شوید.</p>")
                html = html.replace("{% if success %}", "").replace("{% elif error %}", "").replace("{% endif %}", "")
                return (html, 200, {"Content-Type": "text/html; charset=utf-8"})
            else:
                html = render_template("register.html")
                html = html.replace(
                    "{% if success %}{% elif error %}<p class='error'>❌ نام کاربری تکراری است.</p>{% endif %}",
                    "<p class='error'>❌ نام کاربری تکراری است.</p>")
                html = html.replace("{% if success %}", "").replace("{% elif error %}", "").replace("{% endif %}", "")
                return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

        html = render_template("register.html")
        html = html.replace("{% if success %}", "").replace("{% elif error %}", "").replace("{% endif %}", "")
        return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

    # ------------------- فرم درج داده هواشناسی -------------------
    if path == "/add-weather":
        if method == "POST" and body:
            import urllib.parse
            data = urllib.parse.parse_qs(body)
            station_name = data.get('station_name', [''])[0]
            temperature = float(data.get('temperature', [0])[0]) if data.get('temperature', [''])[0] else None
            humidity = float(data.get('humidity', [0])[0]) if data.get('humidity', [''])[0] else None
            pressure = float(data.get('pressure', [0])[0]) if data.get('pressure', [''])[0] else None
            wind_speed = float(data.get('wind_speed', [0])[0]) if data.get('wind_speed', [''])[0] else None
            forecast_date = data.get('forecast_date', [''])[0]
            recorded_by = data.get('recorded_by', [''])[0]

            if station_name and recorded_by:
                save_weather_data(station_name, temperature, humidity, pressure, wind_speed, forecast_date, recorded_by)
                html = render_template("add_weather.html")
                html = html.replace(
                    "{% if success %}<p class='success'>✅ داده هواشناسی با موفقیت ثبت شد.</p>{% elif error %}{% endif %}",
                    "<p class='success'>✅ داده هواشناسی با موفقیت ثبت شد.</p>")
                html = html.replace("{% if success %}", "").replace("{% elif error %}", "").replace("{% endif %}", "")
                return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

        html = render_template("add_weather.html")
        html = html.replace("{% if success %}", "").replace("{% elif error %}", "").replace("{% endif %}", "")
        return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

    # ------------------- مسیر درباره ما -------------------
    if path == "/about":
        html = render_template("about.html")
        if html:
            return (html, 200, {"Content-Type": "text/html; charset=utf-8"})
        return ("Template about.html not found", 500, {"Content-Type": "text/plain"})

    # ------------------- API نمونه -------------------
    if path == "/api/status":
        data = {"project": "weather_platform", "status": "ok"}
        return (json.dumps(data, ensure_ascii=False), 200, {"Content-Type": "application/json"})

    # ------------------- 404 -------------------
    return ("Not Found", 404, {"Content-Type": "text/plain; charset=utf-8"})