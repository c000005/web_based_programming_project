# web_based_programming_project/weather_platform/settings.py
from pathlib import Path
import importlib.util

DB_NAME = 'weather_platform.db'

BASE_DIR = Path(__file__).resolve().parent

# db route on project directory
DB_PATH = BASE_DIR / DB_NAME

TEMPLATE_DIR = BASE_DIR / "templates"

STATIC_DIR = BASE_DIR / "static"
STATIC_URL_PREFIX = "/static/" # URL prefix for static files