# web_based_programming_project/weather_platform/core/permissions.py

ROLES = {
    'admin': {
        'can_manage_users': True,
        'can_manage_products': True,
        'can_manage_messages': True,
        'can_manage_reports': True,
        'can_view_all': True,
        'can_add_weather': True,
        'can_edit_products': True,
        'can_edit_users': True,
    },
    'analyst': {
        'can_manage_users': False,
        'can_manage_products': False,
        'can_manage_messages': False,
        'can_manage_reports': True,
        'can_view_all': True,
        'can_add_weather': True,
        'can_edit_products': False,
        'can_edit_users': False,
    },
    'viewer': {
        'can_manage_users': False,
        'can_manage_products': False,
        'can_manage_messages': False,
        'can_manage_reports': False,
        'can_view_all': True,
        'can_add_weather': False,
        'can_edit_products': False,
        'can_edit_users': False,
    }
}


def has_permission(user, permission):
    """Check if user has a specific permission"""
    if not user:
        return False
    role = user.get('role', 'viewer')
    return ROLES.get(role, {}).get(permission, False)


def is_admin(user):
    """Check if user is admin"""
    return user and user.get('role') == 'admin'


def is_analyst(user):
    """Check if user is analyst"""
    return user and user.get('role') == 'analyst'


def is_viewer(user):
    """Check if user is viewer"""
    return user and user.get('role') == 'viewer'


def require_permission(permission):
    """Decorator to require a permission"""
    def decorator(func):
        def wrapper(path, headers, *args, **kwargs):
            from controllers.auth_controller import get_current_user_from_headers
            user = get_current_user_from_headers(headers)
            if not user:
                from controllers.base_controller import render_error_page
                return render_error_page(401, "لطفاً برای دسترسی به این صفحه وارد شوید.")
            if not has_permission(user, permission):
                from controllers.base_controller import render_error_page
                return render_error_page(403, "شما دسترسی لازم برای مشاهده این صفحه را ندارید.")
            return func(path, headers, *args, **kwargs)
        return wrapper
    return decorator