# web_based_programming_project/weather_platform/controllers/weather_controller.py

from .base_controller import render_template, render_error_page, get_db_connection, parse_form_data


def handle_add_weather_get(headers=None, user_display=""):
    """Show add weather form"""
    html = render_template("add_weather.html", {
        "title": "ثبت داده هواشناسی",
        "user_display": user_display
    })
    if html:
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}
    return render_error_page(500, "Template add_weather.html not found")


def handle_add_weather_post(body, headers=None):
    """Process weather data addition"""
    form_data = parse_form_data(body)
    station_code = form_data.get('station_code', '').strip()
    city_name = form_data.get('city_name', '').strip()
    country = form_data.get('country', '').strip()
    record_date = form_data.get('record_date', '')
    temperature = form_data.get('temperature', '')
    humidity = form_data.get('humidity', '')
    pressure = form_data.get('pressure', '')
    wind_speed = form_data.get('wind_speed', '')
    weather_condition = form_data.get('weather_condition', '').strip()

    if not station_code or not city_name or not country or not record_date:
        return render_error_page(400, "کد ایستگاه، نام شهر، کشور و تاریخ ثبت الزامی هستند")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       INSERT INTO weather_data (station_code, city_name, country, record_date,
                                                 temperature_celsius, humidity_percent, pressure_hpa,
                                                 wind_speed_ms, weather_condition)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ''', (station_code, city_name, country, record_date,
                             float(temperature) if temperature else None,
                             float(humidity) if humidity else None,
                             float(pressure) if pressure else None,
                             float(wind_speed) if wind_speed else None,
                             weather_condition))
        conn.commit()
        conn.close()
        return '<p style="color:green">✅ Weather data saved successfully!</p>', 200, {
            "Content-Type": "text/html; charset=utf-8"}
    except Exception as e:
        return render_error_page(500, f"خطا در ذخیره داده هواشناسی: {e}")


def handle_weather_list(headers=None):
    """Show weather data list"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT id, station_code, city_name, country, record_date,
                              temperature_celsius, humidity_percent, pressure_hpa,
                              wind_speed_ms, weather_condition
                       FROM weather_data
                       ORDER BY record_date DESC LIMIT 50
                       ''')
        weather_data = cursor.fetchall()
        conn.close()

        table_rows = ""
        for wd in weather_data:
            table_rows += f"""
            <tr>
                <td>{wd['id']}</td>
                <td>{wd['station_code']}</td>
                <td>{wd['city_name']}</td>
                <td>{wd['country']}</td>
                <td>{wd['record_date']}</td>
                <td>{wd['temperature_celsius'] if wd['temperature_celsius'] else '-'}</td>
                <td>{wd['humidity_percent'] if wd['humidity_percent'] else '-'}</td>
                <td>{wd['pressure_hpa'] if wd['pressure_hpa'] else '-'}</td>
                <td>{wd['wind_speed_ms'] if wd['wind_speed_ms'] else '-'}</td>
                <td>{wd['weather_condition'] or '-'}</td>
            </tr>
            """

        html = render_template("weather_list.html", {
            "title": "داده‌های هواشناسی",
            "weather_rows": table_rows,
            "user_display": user_display
        })
        if html:
            return html, 200, {"Content-Type": "text/html; charset=utf-8"}
        return render_error_page(500, "Template weather_list.html not found")
    except Exception as e:
        return render_error_page(500, f"خطا در دریافت داده‌های هواشناسی: {e}")