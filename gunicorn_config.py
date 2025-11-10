def post_request(worker, req, environ, resp):
    resp.headers['Server'] = 'undisclosed'