# project2/controllers/product_controller.py
import sqlite3
import settings
from core import response


def get_all_products():
    """Get all active products"""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE is_deleted = 0 ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_product(product_id):
    """Get a single product by ID"""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ? AND is_deleted = 0', (product_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_product(data):
    """Add a new product"""
    name = data.get('name', [''])[0]
    price = data.get('price', ['0'])[0]
    description = data.get('description', [''])[0]

    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO products (name, price, description)
                   VALUES (?, ?, ?)
                   ''', (name, price, description))
    conn.commit()
    conn.close()

    return True


def update_product(product_id, data):
    """Update a product"""
    name = data.get('name', [''])[0]
    price = data.get('price', ['0'])[0]
    description = data.get('description', [''])[0]

    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
                   UPDATE products
                   SET name        = ?,
                       price       = ?,
                       description = ?
                   WHERE id = ?
                   ''', (name, price, description, product_id))
    conn.commit()
    conn.close()

    return True


def delete_product(product_id):
    """Soft delete a product"""
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET is_deleted = 1 WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

    return True