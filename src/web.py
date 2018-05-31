#!/usr/bin/env python
# Thu May 31 09:15:45 CST 2018

import os
import sys

import re
import Cookie
import BaseHTTPServer
import urlparse
import shutil

import chess

STATIC_HOME = os.path.join(os.path.dirname(__file__), "../static")


MIME_MAPPING = {
    "css": "text/css",
    "js": "application/x-javascript",
    "html": "text/html",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif"
}


class HTTPRequest(object):
    def __init__(self, context, path, groups, cookie, args, data, method):
        self.context = context
        self.path = path
        self.groups = groups
        self.cookie = cookie
        self.args = args
        self.data = data
        self.method = method


class HTTPResponse(object):
    def __init__(self, status, headers, body):
        self.status = status
        self.headers = headers
        self.body = body


def handle_home_page(req):
    headers = {"Content-Type": "text/html; charset=utf-8",
                "Location": "/room/123"}
    return HTTPResponse(307, headers, None)


def handle_room(req):
    room_number = int(req.groups[0])
    headers = {"Content-Type": "text/html; charset=utf-8"}
    return HTTPResponse(200, headers,
            "<html><body>welcom to room %d, your args is %s, your cookie is %s</body></html>" % \
                    (room_number, str(req.args), req.cookie.output()))


def handle_404(req):
    header = {"Content-Type": "text/plain; charset=utf-8"}
    return HTTPResponse(404, header, "nothing here, you'r using %d" % (req.method))


def handle_static(req):
    path = os.path.join(STATIC_HOME, req.groups[0])
    parts = os.path.basename(path).split(".")

    if len(parts) == 1 or not os.path.isfile(path):
        return handle_404(req)

    if MIME_MAPPING.get(parts[-1]) is None:
        header = {"Content-Type": "application/octet-stream"}
    else:
        header = {"Content-Type": MIME_MAPPING[parts[-1]]}

    return HTTPResponse(200, header, open(path))


def is_match_all(pattern, string):
    """ return groups on match all """
    m = pattern.match(string)
    if m is None or m.end() != len(string):
        return None

    return m.groups()


def route(route_info, method, path):
    for expected_method, exp, fn in route_info:
        groups = is_match_all(exp, path)
        if groups is not None and (method == expected_method or expected_method == HTTPServer.ANY):
            return fn, groups

    return None, None



class HTTPHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def is_file(self, obj):
        fn_type = type(self.__init__)
        if hasattr(obj, "read") and hasattr(obj, "close"):
            return True
        return False

    def _set_return(self, status, headers, body):
        self.send_response(status)

        for k, v in headers.items():
            self.send_header(k, v)

        self.end_headers()

        if body is not None:
            if isinstance(body, str):
                self.wfile.write(body)
            elif self.is_file(body):
                try:
                    shutil.copyfileobj(body, self.wfile)
                finally:
                    body.close()

    def process(self, method):
        context = self.server.context
        parse_result = urlparse.urlparse(self.path)
        path = os.path.abspath(parse_result.path)

        fn, groups = route(context.route_info, method, path)
        if fn is None:
            self._set_return(404, {"Content-Type": "text/plain; charset=utf-8"}, "nothing here")
            return

        args = {}
        for k, v in urlparse.parse_qsl(parse_result.params):
            args[k] = v
        for k, v in urlparse.parse_qsl(parse_result.query):
            args[k] = v

        if self.headers.get("Content-Length") is not None:
            length = int(self.headers["Content-Length"])
            data = self.rfile.read(length)
        else:
            data = ""

        cookie_data = self.headers.get("Cookie")
        if cookie_data is not None:
            cookie = Cookie.SimpleCookie(cookie_data)
        else:
            cookie = Cookie.SimpleCookie()

        request = HTTPRequest(context, path, groups, cookie, args, data, method)

        resp = fn(request)

        self._set_return(resp.status, resp.headers, resp.body)

    def do_GET(self):
        self.process(HTTPServer.GET)

    def do_PUT(self):
        self.process(HTTPServer.PUT)

    def do_POST(self):
        self.process(HTTPServer.POST)

    def do_HEAD(self):
        self.process(HTTPServer.HEAD)

    def do_PATCH(self):
        self.process(HTTPServer.PATCH)

    def do_DELETE(self):
        self.process(HTTPServer.DELETE)

    def do_OPTIONS(self):
        self.process(HTTPServer.OPTIONS)


class HTTPContext(object):
    """ member of this instance should be thread safe """
    def __init__(self, route_info, chess_session_class, rooms_info, uid_counter):
        self.route_info = route_info
        self.chess_session_class = chess_session_class
        self.rooms_info = rooms_info
        self.uid_counter = uid_counter


class HTTPServer(BaseHTTPServer.HTTPServer):
    GET, PUT, POST, HEAD, PATCH, DELETE, OPTIONS, ANY = xrange(8)

    def __init__(self, *args, **kw):
        BaseHTTPServer.HTTPServer.__init__(self, *args, **kw)
        route_info = (
                (HTTPServer.GET, re.compile("/"), handle_home_page),
                (HTTPServer.GET, re.compile("/room/([0-9]+)"), handle_room),
                (HTTPServer.GET, re.compile("/static/(.*)"), handle_static),
                (HTTPServer.ANY, re.compile(".*"), handle_404)
                )

        # TODO implement cookie and session handler
        self.context = HTTPContext(route_info, chess.Session, None, None)


def run(server_class=HTTPServer, handler_class=HTTPHandler, port=8080):
    server_address = ("127.0.0.1", port)
    httpd = server_class(server_address, handler_class)
    print "Starting httpd at %d..." % (port)
    httpd.serve_forever()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        run(port=int(sys.argv[1]))
    else:
        run()
