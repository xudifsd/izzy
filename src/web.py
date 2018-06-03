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
import json

log = logging.getLogger("web")

import jinja2

import chess
import persist

STATIC_HOME = os.path.join(os.path.dirname(__file__), "../static")
TEMPLATE_HOME = os.path.join(os.path.dirname(__file__), "../template")

STORE_PATH = "data/sessions.data"


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
    def __init__(self, status, headers=None, body=None, cookie=None):
        self.status = status
        self.headers = headers
        self.body = body
        self.cookie = cookie


def redirect(url, cookie=None, status=307):
    headers = {"Content-Type": "text/html; charset=utf-8",
                "Location": url}
    return HTTPResponse(status, headers, None, cookie)


def render_template(template_file_name, *args, **kwargs):
    tpl_path = os.path.join(TEMPLATE_HOME, template_file_name)
    with open(tpl_path, "r") as f:
        content = f.read()

    return jinja2.Environment().from_string(content).render(*args, **kwargs)


def handle_home_page(req):
    user_name = req.context.uid_handler.get_user_name(req.cookie)
    if user_name is None:
        log.debug("user is not logged in")
        return redirect("/static/login.html")

    headers = {"Content-Type": "text/html; charset=utf-8"}

    rooms = req.context.room_manager.list_waiting_room()
    body = render_template("home.tpl", rooms=rooms)
    log.debug("user %s logged in, get rooms %s", user_name, rooms)

    return HTTPResponse(200, headers, body)


def handle_login(req):
    user_name = req.args.get("name")
    if user_name is None:
        return redirect("/static/login.html", status=303)

    new_id = req.context.uid_handler.gen_new_id(user_name)
    req.cookie["uid"] = str(new_id)
    return redirect("/", cookie=req.cookie, status=303)


def handle_new_room(req):
    user_name = req.context.uid_handler.get_user_name(req.cookie)
    if user_name is None:
        return redirect("/static/login.html", status=303)

    room_id = req.context.room_manager.new_room(user_name)
    return redirect("/room/%d/" % (room_id), cookie=req.cookie, status=303)


def get_user_name_room(req):
    user_name = req.context.uid_handler.get_user_name(req.cookie)
    if user_name is None:
        return None, None

    room_id = int(req.groups[0])

    room = req.context.room_manager.get_room(room_id)

    return user_name, room


def handle_room(req):
    user_name, room = get_user_name_room(req)

    if user_name is None or room is None:
        return redirect("/")

    headers = {"Content-Type": "text/html; charset=utf-8"}

    add_rtn = room.add_player(user_name)

    if add_rtn == Room.ADD_OK or add_rtn == Room.ADD_ALREADY_IN:
        log.debug("user going into room %d", room.id)
        body = render_template("room.tpl", room_id=room.id)
        return HTTPResponse(200, headers, body)
    else:
        # add_rtn is ADD_FULL
        return HTTPResponse(200, headers,
                "<html><body>%s, room is full, room status %s</body></html>" % \
                        (user_name, json.dumps(room.status())))


def handle_room_status(req):
    user_name, room = get_user_name_room(req)

    headers = {"Content-Type": "application/json"}

    if room is None:
        return HTTPResponse(404)

    return HTTPResponse(200, headers, json.dumps(room.status()))


def handle_get_my_name(req):
    user_name = req.context.uid_handler.get_user_name(req.cookie)
    if user_name is None:
        return HTTPResponse(404)
    else:
        headers = {"Content-Type": "application/json; charset=utf-8"}
        return HTTPResponse(200, headers, json.dumps({"name": user_name}))



def handle_room_move(req):
    user_name, room = get_user_name_room(req)

    if room is None:
        return HTTPResponse(404)

    if user_name is None:
        return HTTPResponse(403)

    if user_name is None or room is None:
        return HTTPResponse(404)

    row, col = req.args.get("row"), req.args.get("col")
    if row is None or row is None or not row.isdigit() or not col.isdigit():
        return HTTPResponse(400)

    row, col = int(row), int(col)

    if room.session is None:
        log.debug("session is not established")
        return HTTPResponse(400)

    rtn = room.session.move(row, col, user_name)

    headers = {"Content-Type": "application/json; charset=utf-8"}

    if rtn == chess.Session.MOVE_OK:
        code = 200
        if room.session.get_winner() is not None:
            req.context.persist_manager.persist(room.session.serialize())
            status = "finished"
        else:
            status = "ok"
    else:
        log.debug("move not ok, status %d", rtn)
        if rtn == chess.Session.MOVE_INVALID:
            code = 400
            status = "move_invalid"
        elif rtn == chess.Session.MOVE_NOT_PLAYER:
            code = 401
            status = "not_player"
        elif rtn == chess.Session.MOVE_NOT_YOUR_TURN:
            code = 403
            status = "not_your_turn"

    return HTTPResponse(code, headers, json.dumps({"status": status}))


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
    def _is_file(self, obj):
        fn_type = type(self.__init__)
        if hasattr(obj, "read") and hasattr(obj, "close"):
            return True
        return False

    def _set_return(self, resp):
        body = resp.body

        self.send_response(resp.status)

        if resp.headers is not None:
            for k, v in resp.headers.items():
                self.send_header(k, v)

        if resp.cookie is not None:
            for k, v in resp.cookie.items():
                self.send_header("Set-Cookie", "%s=%s" % (str(k), str(v.coded_value)))


        if body is not None:
            if isinstance(body, str) or isinstance(body, unicode):
                log.debug("get str response body, length is %d", len(body))
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()

                self.wfile.write(body)
            elif self._is_file(body):
                self.end_headers()
                try:
                    shutil.copyfileobj(body, self.wfile)
                finally:
                    body.close()
            else:
                self.end_headers()
                log.warn("unknown body %r", body)


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

        content_type = self.headers.get("Content-Type")
        if content_type is not None and content_type.startswith("application/x-www-form-urlencoded"):
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


class Room(object):
    ADD_OK, ADD_ALREADY_IN, ADD_FULL = range(3)

    def __init__(self, id):
        self.id = id
        self.lock = threading.RLock()
        self.player_names = []
        self.session = None

    def add_player(self, name):
        with self.lock:
            if name in self.player_names:
                return Room.ADD_ALREADY_IN
            elif len(self.player_names) >= 2:
                return Room.ADD_FULL

            self.player_names.append(name)
            if len(self.player_names) == 2:
                self.session = chess.Session(self.player_names[0], self.player_names[1], False, False)
            return Room.ADD_OK

    def status(self):
        with self.lock:
            result = {"id": self.id, "players": self.player_names[:]}
            if self.session is None:
                result["status"] = "waiting"
            else:
                result["table"] = self.session.table.to_array()
                if self.session.get_winner() is not None:
                    result["status"] = "finished"
                    result["winner"] = self.session.get_winner()
                else:
                    result["status"] = "playing"
                    result["current"] = self.session.get_current_player_name()

            return result



class RoomManager(object):
    def __init__(self):
        self.lock = threading.RLock()
        self.rooms = []

    def new_room(self, user_name):
        with self.lock:
            id = len(self.rooms)
            room = Room(id)
            self.rooms.append(room)
            room.add_player(user_name)
            return id

    def get_room(self, room_id):
        with self.lock:
            if room_id < 0 or room_id >= len(self.rooms):
                return None
            return self.rooms[room_id]

    def list_waiting_room(self):
        with self.lock:
            result = []
            return filter(lambda s: s["status"] == "waiting",
                    map(lambda x: x.status(), self.rooms))


class HTTPContext(object):
    """ member of this instance should be thread safe """
    def __init__(self, route_info, room_manager, uid_handler, persist_manager):
        self.route_info = route_info
        self.room_manager = room_manager
        self.uid_handler = uid_handler
        self.persist_manager = persist_manager


class HTTPServer(BaseHTTPServer.HTTPServer):
    GET, PUT, POST, HEAD, PATCH, DELETE, OPTIONS, ANY = xrange(8)

    def __init__(self, *args, **kw):
        BaseHTTPServer.HTTPServer.__init__(self, *args, **kw)
        route_info = (
                (HTTPServer.GET, re.compile("/"), handle_home_page),
                (HTTPServer.POST, re.compile("/"), handle_login),
                (HTTPServer.GET, re.compile("/new-room"), handle_new_room),
                (HTTPServer.GET, re.compile("/my-name"), handle_get_my_name),
                (HTTPServer.GET, re.compile("/room/([0-9]+)"), handle_room),
                (HTTPServer.GET, re.compile("/room/([0-9]+)/status"), handle_room_status),
                (HTTPServer.POST, re.compile("/room/([0-9]+)/move"), handle_room_move),
                (HTTPServer.GET, re.compile("/static/(.*)"), handle_static),
                (HTTPServer.ANY, re.compile(".*"), handle_404)
                )

        self.persist_manager = persist.PersistManager(STORE_PATH)
        self.persist_manager.start()
        self.context = HTTPContext(route_info, RoomManager(), UidHandler(), self.persist_manager)

    def serve(self):
        while True:
            try:
                self.handle_request()
            except KeyboardInterrupt:
                self.persist_manager.join()
                break



def run(server_class=HTTPServer, handler_class=HTTPHandler, port=8080):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print "Starting httpd at %d..." % (port)
    httpd.serve()
    return 0


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
            level=logging.DEBUG)
    if len(sys.argv) == 2:
        sys.exit(run(port=int(sys.argv[1])))
    else:
        sys.exit(run())
