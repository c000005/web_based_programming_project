import json

import os

from pathlib import Path

# -------------------------------------

#   تابع کمکی برای لود HTML از فایل

# -------------------------------------

def render_template(filename):

    base_dir = Path(__file__).resolve().parent

    template_path = base_dir / "templates" / filename

    if not template_path.exists():

        return None

    return template_path.read_text(encoding="utf-8")

# -------------------------------------

#   تابع اصلی مسیریابی

# -------------------------------------

def route(path, method, body):

#    _load_db_setup_and_run()

    # --------------------------

    #  صفحه اصلی (index.html)

    # --------------------------

    if path == "/":

        html = render_template("index.html")

        if html:

            return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

        return ("Template index.html not found", 500, {"Content-Type": "text/plain"})

    # --------------------------

    #  مسیر contact

    # --------------------------

    if path == "/contact":

        html = render_template("contact.html")

        if html:

            return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

        return ("Template contact.html not found", 500, {"Content-Type": "text/plain"})

    # --------------------------

    #  مسیر about

    # --------------------------

    if path == "/about":

        html = render_template("about.html")

        if html:

            return (html, 200, {"Content-Type": "text/html; charset=utf-8"})

        return ("Template about.html not found", 500, {"Content-Type": "text/plain"})

    # --------------------------

    #  مثال JSON

    # --------------------------

    if path == "/api/status":

        data = {"project": "project1", "status": "ok"}

        return (json.dumps(data, ensure_ascii=False), 200,

                {"Content-Type": "application/json"})

    # --------------------------

    #  مثال POST echo

    # --------------------------

    if path == "/api/echo" and method == "POST":

        data = {"received": body, "length": len(body)}

        return (json.dumps(data, ensure_ascii=False), 200,

                {"Content-Type": "application/json"})

    # --------------------------

    # مسیر نامعتبر

    # --------------------------

    return ("Not Found (inside project1)", 404,

            {"Content-Type": "text/plain; charset=utf-8"})