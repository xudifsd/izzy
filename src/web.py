#!/usr/bin/env python
# Thu May 31 09:15:45 CST 2018

import os
import sys

import re
import Cookie
import BaseHTTPServer
import urlparse
import shutil
import threading
import logging

log = logging.getLogger("web")

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
    def __init__(self, headers, context, path, groups, cookie, args, data, method):
        self.headers = headers
        self.context = context
        self.path = path
        self.groups = groups
        self.cookie = cookie
        self.args = args
        self.data = data
        self.method = method


class HTTPResponse(object):
    def __init__(self, status, headers, body, cookie):
        self.status = status
        self.headers = headers
        self.body = body
        self.cookie = cookie


def redirect(url, cookie=None, status=307):
    headers = {"Content-Type": "text/html; charset=utf-8",
                "Location": url}
    return HTTPResponse(status, headers, None, cookie)


def handle_home_page(req):
    return redirect("/static/home.html")


def handle_login(req):
    if req.args.get("name") is None:
        return redirect("/static/home.html")

    new_id = req.context.uid_handler.gen_new_id(req.args.get("name"))
    req.cookie["uid"] = str(new_id)
    return redirect("/room/123", cookie=req.cookie, status=303)


def handle_room(req):
    user_name = req.context.uid_handler.get_user_name(req.cookie)
    if user_name is None:
        return redirect("/")

    room_number = int(req.groups[0])
    headers = {"Content-Type": "text/html; charset=utf-8"}

    return HTTPResponse(200, headers,
            "<html><body>%s, welcom to room %d</body></html>" % \
                    (user_name, room_number), req.cookie)


def handle_404(req):
    header = {"Content-Type": "text/plain; charset=utf-8"}
    return HTTPResponse(404, header, "nothing here, you'r using %d" % (req.method), req.cookie)


def handle_static(req):
    path = os.path.join(STATIC_HOME, req.groups[0])
    parts = os.path.basename(path).split(".")

    if len(parts) == 1 or not os.path.isfile(path):
        return handle_404(req)

    if MIME_MAPPING.get(parts[-1]) is None:
        header = {"Content-Type": "application/octet-stream"}
    else:
        header = {"Content-Type": MIME_MAPPING[parts[-1]]}

    return HTTPResponse(200, header, open(path), req.cookie)


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
    def _is_file(self, obj):
        fn_type = type(self.__init__)
        if hasattr(obj, "read") and hasattr(obj, "close"):
            return True
        return False

    def _set_return(self, resp):
        body = resp.body

        self.send_response(resp.status)

        for k, v in resp.headers.items():
            self.send_header(k, v)

        if resp.cookie is not None:
            for k, v in resp.cookie.items():
                self.send_header("Set-Cookie", "%s=%s" % (str(k), str(v.coded_value)))

        self.end_headers()

        if body is not None:
            if isinstance(body, str):
                self.wfile.write(body)
            elif self._is_file(body):
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
            self._set_return(HTTPResponse(404, {"Content-Type": "text/plain; charset=utf-8"}, "nothing here"), None)
            return

        if self.headers.get("Content-Length") is not None:
            length = int(self.headers["Content-Length"])
            data = self.rfile.read(length)
        else:
            data = ""

        args = {}
        for k, v in urlparse.parse_qsl(parse_result.params):
            args[k] = v
        for k, v in urlparse.parse_qsl(parse_result.query):
            args[k] = v

        if self.headers.get("Content-Type") == "application/x-www-form-urlencoded":
            for k, v in urlparse.parse_qsl(data):
                args[k] = v

        cookie_data = self.headers.get("Cookie")
        if cookie_data is not None:
            cookie = Cookie.SimpleCookie(cookie_data)
        else:
            cookie = Cookie.SimpleCookie()

        request = HTTPRequest(self.headers, context, path, groups, cookie, args, data, method)

        self._set_return(fn(request))

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


class UidHandler(object):
    def __init__(self):
        self.lock = threading.RLock()
        self.array = []

    def get_user_name(self, cookie):
        if cookie.get("uid") is None or not cookie.get("uid").value.isdigit():
            return None

        id = int(cookie.get("uid").value)

        with self.lock:
            if id < 0 or id >= len(self.array):
                return None
            return self.array[id]

    def gen_new_id(self, name):
        with self.lock:
            self.array.append(name)
            return len(self.array) - 1


class HTTPContext(object):
    """ member of this instance should be thread safe """
    def __init__(self, route_info, chess_session_class, rooms_info, uid_handler):
        self.route_info = route_info
        self.chess_session_class = chess_session_class
        self.rooms_info = rooms_info
        self.uid_handler = uid_handler


class HTTPServer(BaseHTTPServer.HTTPServer):
    GET, PUT, POST, HEAD, PATCH, DELETE, OPTIONS, ANY = xrange(8)

    def __init__(self, *args, **kw):
        BaseHTTPServer.HTTPServer.__init__(self, *args, **kw)
        route_info = (
                (HTTPServer.GET, re.compile("/"), handle_home_page),
                (HTTPServer.POST, re.compile("/"), handle_login),
                (HTTPServer.GET, re.compile("/room/([0-9]+)"), handle_room),
                (HTTPServer.GET, re.compile("/static/(.*)"), handle_static),
                (HTTPServer.ANY, re.compile(".*"), handle_404)
                )

        # TODO implement cookie and session handler
        self.context = HTTPContext(route_info, chess.Session, None, UidHandler())


def run(server_class=HTTPServer, handler_class=HTTPHandler, port=8080):
    server_address = ("127.0.0.1", port)
    httpd = server_class(server_address, handler_class)
    print "Starting httpd at %d..." % (port)
    httpd.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
            level=logging.INFO)
    if len(sys.argv) == 2:
        run(port=int(sys.argv[1]))
    else:
        run()
