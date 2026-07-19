# web_based_programming_project/weather_platform/core/cookie.py
def make_set_cookie_header(name, value, path="/", max_age=None, http_only=True):
    """Create Set-Cookie header value"""
    cookie = f"{name}={value}; Path={path}"
    if http_only:
        cookie += "; HttpOnly"
    if max_age:
        cookie += f"; Max-Age={max_age}"
    return cookie

def set_cookie(name, value, headers=None, **kwargs):
    """Set cookie in response headers"""
    if headers is None:
        headers = {}
    headers["Set-Cookie"] = make_set_cookie_header(name, value, **kwargs)
    return headers

def clear_cookie(name, headers=None, path="/"):
    """Clear cookie by setting expired date"""
    if headers is None:
        headers = {}
    headers["Set-Cookie"] = f"{name}=; Path={path}; Max-Age=0; HttpOnly"
    return headers