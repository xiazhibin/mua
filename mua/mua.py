import re


class Mua(object):
    def __init__(self):
        self.routers = []

    @staticmethod
    def bulid_router_rex(router):
        pattern = re.sub("(<\w+>)", r"(?P\1.+)", router)
        pattern_str = "^{}$".format(pattern)
        return re.compile(pattern_str)

    def route(self, route_str):
        def decorator(f):
            route_pattern = self.bulid_router_rex(route_str)
            self.routers.append((route_pattern, f))
            return f
        return decorator

    def get_match_route(self, path):
        for pattern, view_func in self.routers:
            m = pattern.match(path)
            if m:
                return m.groupdict(), view_func

    def __call__(self, environ, start_response):
        request_method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        route_match = self.get_match_route(path)
        if route_match:
            status = '200 OK'
            kwargs, view_function = route_match
            result_str = view_function(**kwargs)
        else:
            status = '404 Not Found'
            result_str = 'Route "{}"" has not been registered'.format(path)
        # bt = bytes(result_str, encoding="utf-8")
        response_headers = [('Content-Type', 'text/plain')]
        start_response(status, response_headers)
        return result_str

    def run(self, server_ip='127.0.0.1', port=8888):
        from .webserver import run_simple
        run_simple(server_ip, port, self)
