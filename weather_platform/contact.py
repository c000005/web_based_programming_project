from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs # برای تجزیه داده‌های فرم

# تنظیمات سرور
HOST_NAME = '127.0.0.1'
PORT_NUMBER = 8000

class SimpleFormReceiver(BaseHTTPRequestHandler):

    # متد do_POST مسئول دریافت داده‌های ارسالی با متد POST است
    def do_POST(self):
        # بررسی می‌کنیم که آیا درخواست به مسیر اصلی '/' آمده است
        # (در عمل، فرم ما داده‌ها را به این آدرس می‌فرستد)
        if self.path == '/':
            # خواندن طول محتوای درخواست از هدر
            content_length = int(self.headers['Content-Length'])
            # خواندن داده‌های خام فرم از بدنه درخواست
            post_data_bytes = self.rfile.read(content_length)

            # تبدیل داده‌های بایتی به رشته و تجزیه آن‌ها
            # parse_qs داده‌ها را به صورت دیکشنری از لیست‌ها برمی‌گرداند
            # مثال: {'user_name': ['مقدار نام'], 'user_email': ['مقدار ایمیل']}
            parsed_data = parse_qs(post_data_bytes.decode('utf-8'))

            # چاپ اطلاعات دریافتی در کنسول سرور
            print("-" * 40)
            print("داده‌های فرم دریافت شد:")
            # برای هر کلید (اسم فیلد) و مقدار آن در دیکشنری parsed_data
            for key, value in parsed_data.items():
                # value یک لیست است، پس اولین عنصر آن را چاپ می‌کنیم
                print(f"  {key}: {value[0]}")
            print("-" * 40)

            # چون هدف فقط چاپ کردن است، یک پاسخ ساده به مرورگر می‌دهیم
            # این پاسخ فقط برای این است که مرورگر منتظر نماند
            self.send_response(200) # کد وضعیت موفقیت
            self.send_header('Content-type', 'text/plain; charset=utf-8') # محتوا متن ساده است
            self.end_headers()
            self.wfile.write("اطلاعات با موفقیت دریافت و پردازش شد.".encode('utf-8'))

        else:
            # اگر مسیر دیگری درخواست شود (که نباید اتفاق بیفتد)
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("مسیر پیدا نشد.".encode('utf-8'))

# تابع برای اجرای سرور
def run_server(port=PORT_NUMBER):
    server_address = (HOST_NAME, port)
    httpd = HTTPServer(server_address, SimpleFormReceiver)
    print(f"سرور در حال اجرا روی http://{HOST_NAME}:{port}")
    print("برای توقف، Ctrl+C را فشار دهید.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print("سرور متوقف شد.")

if __name__ == "__main__":
    run_server()
