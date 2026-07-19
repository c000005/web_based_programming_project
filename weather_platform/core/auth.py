# web_based_programming_project/weather_platform/core/auth.py
import uuid
import sqlite3
from datetime import datetime, timedelta
import settings


def create_session(user_id):
    """Create a new session for a user"""
    session_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(days=1)

    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
                   INSERT INTO sessions (id, user_id, expires_at)
                   VALUES (?, ?, ?)
                   ''', (session_id, user_id, expires_at.isoformat()))
    conn.commit()
    conn.close()

    return session_id


def get_user_by_session(session_id):
    """Get user data from session ID"""
    if not session_id:
        return None

    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT u.id, u.username, u.email, u.full_name, u.role, u.is_active
                   FROM sessions s
                   JOIN users u ON s.user_id = u.id
                   WHERE s.id = ?
                   AND s.expires_at > datetime('now')
                   ''', (session_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def get_current_user(headers):
    """Get current user from request headers"""
    cookie_header = headers.get('Cookie', '')
    session_id = None

    # Parse cookie
    for cookie in cookie_header.split(';'):
        cookie = cookie.strip()
        if cookie.startswith('session_id='):
            session_id = cookie.split('=', 1)[1]
            break

    if not session_id:
        return None

    return get_user_by_session(session_id)


def is_admin(user):
    """Check if user has admin role"""
    return user and user.get('role') == 'admin'


def delete_session(session_id):
    """Delete a session (logout)"""
    if not session_id:
        return

    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()