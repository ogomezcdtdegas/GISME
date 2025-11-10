def post_request(worker, req, environ, resp):
    # resp.headers is a list of tuples in some environments (like Azure)
    # Remove any existing 'Server' header
    resp.headers = [(k, v) for (k, v) in resp.headers if k.lower() != 'server']
    # Add your custom header
    resp.headers.append(('Server', 'undisclosed'))