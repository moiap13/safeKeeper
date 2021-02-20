#!/usr/bin/env python3
import hashlib
import os
import sys
from flask import Flask, render_template, request, make_response, jsonify, session
from simplecrypt import decrypt
from sqlalchemy import Column, String, BLOB, Integer, create_engine, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_socketio import SocketIO, send, emit, join_room
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import uuid

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

_db_uri = "sqlite:///"
_base = declarative_base()
_engine = None
_sess_db = None
_password = None

clients = []

def initDbInstance():
    global _engine
    _engine = create_engine(_db_uri, echo=False)
    _session = sessionmaker(bind=_engine)
    return _session()

def load_settings(sa_session):
    s = sa_session.query(main.Settings).all()
    return s[0]

@app.route('/db_name')
def index2():
    return session["user_dict"]["db_name"]

@app.route('/uuid')
def index3():
    return "Client uuid : " + session["client_uuid"] #+ " / " + "db_loaded : " + session["db_loaded"]

@socketio.on('connection')
def another_event(uuid):
    session["client_uuid"] = uuid
    join_room(uuid)
    socketio.emit("info", "only for room " + uuid, room=uuid)
    print("new client : %s" % (uuid))

@socketio.on('connected')
def connected():
    print("%s connected" % (request.namespace.socket.sessid))
    clients.append(request.namespace)

@app.route("/droppedfiles", methods=["POST"])
def droppedfiles():
    if request.files:
        data = request.files["databasefile"]
        print("database dir : " + str(DATABASE_DIRECTORY_PATH))

        if not os.path.isdir(DATABASE_DIRECTORY_PATH):
            os.mkdir(DATABASE_DIRECTORY_PATH)

        global _sess_db

        user_dict = {"db_name": str(uuid.uuid4())}
        session["user_dict"] = user_dict
        session["sa_session"] = _sess_db

        data.save(os.path.join(DATABASE_DIRECTORY_PATH, user_dict["db_name"]))

        print("data saved as " + user_dict["db_name"])


        socketio.emit("request_pwd", room=session["client_uuid"], callback=ack_db_pwd)

        global _db_uri
        _db_uri += DATABASE_DIRECTORY_PATH + user_dict["db_name"]

        #TODO: socketIo database loaded

        session["sa_session"] = initDbInstance()

        #TODO: socketIo validating database
        _settings = load_settings(session["sa_session"])
        session["settings"] = _settings
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
    if "logged" in session:
        return "db_loaded"
    else:
        session["logged"] = True
        return render_template('index.html', client_uuid=(session["client_uuid"] if "client_uuid" in session else None))

@app.route('/logout', methods=['GET'])
def my_form_post():
    session_db.engine.execute("delete from sessions where session_id like 'session\::sid'", sid=session.sid)
    session.clear()
    return "logged out"

@app.route('/password', methods=['POST'])
def ack_db_pwd():
    password = request.form['ipt_pwd']

    # TODO: decrypt db
    _hashed_password = hashlib.sha224(bytes(password, encoding='utf-8')).hexdigest()

    if _hashed_password != session["settings"].password:
        raise Exception("wrong password")

    session["db_loaded"] = True

    return decrypt(password, session["settings"].firstname).decode("utf-8")

if __name__ == "__main__":
    socketio.run(app=app, port=13226)

