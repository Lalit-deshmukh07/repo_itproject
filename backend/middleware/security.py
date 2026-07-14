def add_security_headers(response, request_path):
    """Disable caching for authenticated HTML pages that may include personal data."""
    sensitive_paths = {'/profile', '/profile-setup', '/recommendations'}
    if request_path in sensitive_paths:
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response
