#!/usr/bin/env python
# Thu May 31 09:15:45 CST 2018

import os
import sys

import threading
import logging
import json

log = logging.getLogger("web")

import jinja2
from flask import Flask
import flask

import chess
import persist
import izzy

STATIC_HOME = os.path.join(os.path.dirname(__file__), "../static")
TEMPLATE_HOME = os.path.join(os.path.dirname(__file__), "../template")

STORE_PATH = "data/sessions.data"


app = Flask(__name__)


class UidHandler(object):
    def __init__(self):
        self.lock = threading.RLock()
        self.array = []

    def get_user_name(self, uid):
        if uid is None or not uid.isdigit():
            return None

        id = int(uid)

        with self.lock:
            if id < 0 or id >= len(self.array):
                return None
            return self.array[id]

    def gen_new_id(self, name):
        with self.lock:
            self.array.append(name)
            return len(self.array) - 1


class RoomManager(object):
    def __init__(self):
        self.lock = threading.RLock()
        self.rooms = []

    def new_room(self, user_name, izzy):
        with self.lock:
            id = len(self.rooms)
            room = Room(id)
            self.rooms.append(room)
            room.add_player(user_name, False)
            if izzy is not None:
                room.add_ai(izzy)
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


uid_handler = UidHandler()
room_manager = RoomManager()

izzy_ins = izzy.Izzy.new()
sessions = map(lambda data: chess.Session.deserialize(data),
        list(persist.iterate_over_store(STORE_PATH)))
izzy_ins.train(sessions)

persist_manager = persist.PersistManager(STORE_PATH)
persist_manager.start()

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


@app.route("/", methods=["GET"])
def handle_home_page():
    uid = flask.request.cookies.get("uid")
    user_name = uid_handler.get_user_name(uid)
    if user_name is None:
        app.logger.debug("user is not logged in")
        return flask.redirect(flask.url_for("static", filename="login.html")) # status=303

    rooms = room_manager.list_waiting_room()
    app.logger.debug("user %s logged in, get rooms %s", user_name, rooms)

    return flask.render_template("home.tpl", rooms=rooms)


@app.route("/", methods=["POST"])
def handle_login():
    user_name = flask.request.form["name"]
    if user_name is None:
        return flask.redirect("/static/login.html") # status=303

    if user_name == "izzy":
        return flask.make_response("<html><body>izzy is reseved name</body></html>", 400)

    new_id = uid_handler.gen_new_id(user_name)
    resp = flask.make_response(flask.redirect("/")) # status=303
    resp.set_cookie("uid", str(new_id))
    return resp


@app.route("/new-room", methods=["GET"])
def handle_new_room():
    uid = flask.request.cookies.get('uid')
    user_name = uid_handler.get_user_name(uid)
    if user_name is None:
        return flask.redirect(flask.url_for("static", filename='login.html')) # status=303

    if flask.request.args.get("with_ai") in ["True", "true"]:
        izzy = izzy_ins
    else:
        izzy = None

    room_id = room_manager.new_room(user_name, izzy)
    return flask.redirect("/room/%d/" % (room_id)) # status=303

def get_user_name_room(room_id):
    uid = flask.request.cookies.get('uid')
    user_name = uid_handler.get_user_name(uid)
    if user_name is None:
        return None, None

    room = room_manager.get_room(room_id)

    return user_name, room


@app.route("/room/<int:room_id>/", methods=["GET"])
def handle_room(room_id):
    user_name, room = get_user_name_room(room_id)

    if user_name is None or room is None:
        return flask.redirect(flask.url_for("handle_home_page"))

    add_rtn = room.add_player(user_name, False)

    if add_rtn == Room.ADD_OK or add_rtn == Room.ADD_ALREADY_IN:
        app.logger.debug("user going into room %d", room.id)
        return flask.render_template("room.tpl", room_id=room.id)
    else:
        # add_rtn is ADD_FULL
        return flask.make_response("<html><body>%s, room is full, room status %s</body></html>" % \
                        (user_name, json.dumps(room.status())))


@app.route("/room/<int:room_id>/status", methods=["GET"])
def handle_room_status(room_id):
    user_name, room = get_user_name_room(room_id)

    if room is None:
        return "room not found", 404

    resp = flask.make_response(json.dumps(room.status()), 200)
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp


@app.route("/my-name", methods=["GET"])
def handle_get_my_name():
    uid = flask.request.cookies.get('uid')
    user_name = uid_handler.get_user_name(uid)
    if user_name is None:
        return "not logged in", 404
    else:
        resp = flask.make_response(json.dumps({"name": user_name}), 200)
        resp.headers["Content-Type"] = "application/json; charset=utf-8"
        return resp


@app.route("/room/<int:room_id>/move", methods=["POST"])
def handle_room_move(room_id):
    user_name, room = get_user_name_room(room_id)

    if room is None:
        return "room not found", 404

    if user_name is None:
        return "user not logged in", 404

    row, col = flask.request.form["row"], flask.request.form["col"]
    if row is None or row is None or not row.isdigit() or not col.isdigit():
        return "row or col is illegal", 400

    row, col = int(row), int(col)

    if room.session is None:
        return "session is not established", 400

    rtn = room.session.move(row, col, user_name)

    if rtn == chess.Session.MOVE_OK:
        code = 200
        if room.session.get_winner() is not None:
            status = "finished"
        else:
            status = "ok"
            if room.izzy is not None:
                row, col = room.izzy.query(room.session)
                ai_rtn = room.session.move(row, col, "izzy")
                if ai_rtn != chess.Session.MOVE_OK:
                    app.logger.warning("ai move for table %d, row %d, col %d is not ok, rtn %d",
                            room.session.table, row, col, ai_rtn)
    else:
        app.logger.debug("move not ok, status %d", rtn)
        if rtn == chess.Session.MOVE_INVALID:
            code = 400
            status = "move_invalid"
        elif rtn == chess.Session.MOVE_NOT_PLAYER:
            code = 401
            status = "not_player"
        elif rtn == chess.Session.MOVE_NOT_YOUR_TURN:
            code = 403
            status = "not_your_turn"

    if room.session.get_winner() is not None:
        persist_manager.persist(room.session.serialize())
        izzy_ins.train([room.session])

    resp = flask.make_response(json.dumps({"status": status}), code)
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp


class Room(object):
    ADD_OK, ADD_ALREADY_IN, ADD_FULL = range(3)

    def __init__(self, id):
        self.id = id
        self.lock = threading.RLock()
        self.player_names = []
        self.is_ais = []
        self.session = None
        self.izzy = None

    def add_player(self, name, is_ai):
        with self.lock:
            if name in self.player_names:
                return Room.ADD_ALREADY_IN
            elif len(self.player_names) >= 2:
                return Room.ADD_FULL

            self.player_names.append(name)
            self.is_ais.append(is_ai)
            if len(self.player_names) == 2:
                self.session = chess.Session(self.player_names[0], self.player_names[1],
                        self.is_ais[0], self.is_ais[1])
            return Room.ADD_OK

    def add_ai(self, izzy):
        with self.lock:
            rtn = self.add_player("izzy", True)
            if rtn == Room.ADD_OK:
                self.izzy = izzy
            return rtn

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


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
            level=logging.DEBUG)
    if len(sys.argv) == 2:
        sys.exit(run(port=int(sys.argv[1])))
    else:
        sys.exit(run())
