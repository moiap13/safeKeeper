#!/usr/bin/env python3
import hashlib
import os
import sys
import time
from threading import Thread
from multiprocessing import Process

from flask import Flask, render_template, request, make_response, jsonify, session, redirect, url_for
from simplecrypt import decrypt
from sqlalchemy import Column, String, BLOB, Integer, create_engine, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from flask_socketio import SocketIO, send, emit, join_room
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import uuid
import sqlite3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/terminal")

import main


app = Flask(__name__, template_folder="templates")
#app.secret_key = 'any random string'
app.config['SECRET_KEY'] = 'mysecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///session_db'
app.config['SESSION_TYPE'] = 'sqlalchemy'
#app.config['SESSION_PERMANENT'] = False

session_db = SQLAlchemy(app)

app.config['SESSION_SQLALCHEMY'] = session_db

sess = Session(app)

session_db.create_all()

socketio = SocketIO(app, manage_session=False)

CURRENT_DIRECTORY = (os.path.realpath(__file__)).replace(os.path.basename(__file__), "")
DATABASE_DIRECTORIES = "uploaded_databases"
DATABASE_DIRECTORY_PATH = os.path.join(CURRENT_DIRECTORY + DATABASE_DIRECTORIES + "/")

_base = declarative_base()
_engine = None
_sess_db = None
_password = None

clients_db_sessions = {}

def initDbInstance(_db_uri):
    con = sqlite3.connect(_db_uri, check_same_thread=False)
    return con


def load_settings(sa_session):
    return sa_session.cursor().execute("select * from settings").fetchone()

@app.route('/db_name')
def index2():
    return session["user_dict"]["db_name"]

@app.route('/uuid')
def index3():
    return "Client uuid : " + session["d"] #+ " / " + "db_loaded : " + session["db_loaded"]

@socketio.on('connection')
def another_event(uuid):
    if "client_uuid" not in session:
        session["client_uuid"] = uuid
        join_room(uuid)
        socketio.emit("infos", "only for room " + uuid, room=uuid)
        print("new client : %s" % (uuid))

@socketio.on('connected')
def connected():
    print("%s connected" % (request.namespace.socket.sessid))
    clients.append(request.namespace)

@app.route("/droppedfiles", methods=["POST"])
def droppedfiles():
    if request.files and "client_uuid" in session:
        data = request.files["databasefile"]
        print("database dir : " + str(DATABASE_DIRECTORY_PATH))

        if not os.path.isdir(DATABASE_DIRECTORY_PATH):
            os.mkdir(DATABASE_DIRECTORY_PATH)

        clients_db_sessions[session["client_uuid"]] = {}
        clients_db_sessions[session["client_uuid"]]["db_name"] = str(uuid.uuid4())
        data.save(os.path.join(DATABASE_DIRECTORY_PATH, clients_db_sessions[session["client_uuid"]]["db_name"]))

        print("data saved as " + clients_db_sessions[session["client_uuid"]]["db_name"])

        #TODO: socketIo database loaded
        cur_session = initDbInstance(DATABASE_DIRECTORY_PATH + clients_db_sessions[session["client_uuid"]]["db_name"])
        #session["sa_sessio"]= cur_session
        clients_db_sessions[session["client_uuid"]]["cur_session"] = cur_session

        #TODO: socketIo validating database
        _settings = load_settings(clients_db_sessions[session["client_uuid"]]["cur_session"])
        clients_db_sessions[session["client_uuid"]]["settings"] = _settings
        socketio.emit("request_pwd", room=session["client_uuid"], callback=ack_db_pwd)
        return "1"
        #TODO: socketIo ask password

    print(data)

    response = make_response(
        jsonify(
            {'success': True, 'error': ""}
        ),
        200,
    )
    response.headers["Content-Type"] = "application/json"
    return response

@app.route('/')
def index():
    if "client_uuid" in session:
        return "db_loaded"
    else:
        return render_template('index.html', client_uuid=(session["client_uuid"] if "client_uuid" in session else None))

@app.route('/logout', methods=['GET'])
def my_form_post():
    session_db.engine.execute("delete from sessions where session_id like 'session\::sid'", sid=session.sid)
    session.clear()
    return redirect("/")

@app.route('/password', methods=['POST'])
def ack_db_pwd():
    password = request.form['ipt_pwd']

    if password != None:

        # TODO: decrypt db
        _hashed_password = hashlib.sha224(bytes(password, encoding='utf-8')).hexdigest()

        if _hashed_password != clients_db_sessions[session["client_uuid"]]["settings"][2]:
            raise Exception("wrong password")

        clients_db_sessions[session["client_uuid"]]["db_password"] = password

        return redirect(url_for('list_files'))

@app.route("/list_files", methods=["GET"])
def list_files():
    if "client_uuid" in session:
        return render_template('list_files.html', client_uuid=session["client_uuid"])
    else:
        return redirect("/")



@socketio.on('get_data')
def send_data(room):
    join_room(uuid)
    #files = session.query(main.Files).all()
    socketio.emit("infos", "only for room " + room, room=room)
    files = clients_db_sessions[room]["cur_session"].cursor().execute("select * from Files").fetchall()

    begin = time.time()
    def print_files(title):
        if title.split(".")[-1] == "directory":
            title = title[:-10] + "/"
        return title

    def decrypt_file(list, password, file, id):
        file_title = print_files(decrypt(password, file).decode("utf-8"))
        list[id] = file_title

    titles = {}
    threads = []
    for file in files:
        t = Thread(target=decrypt_file, args=(titles, clients_db_sessions[room]["db_password"], file[1], file[0]))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end = time.time()

    print(f"Total runtime of the program is {end - begin}")

    socketio.emit("infos", "hello", room=room)
    socketio.emit("files_data", titles, room=room)

if __name__ == "__main__":
    socketio.run(app=app, port=13226)

