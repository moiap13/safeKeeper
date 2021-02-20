#!/usr/bin/env python3
import os
import sys
from flask import Flask, render_template, request, make_response, jsonify, session
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

session_db = SQLAlchemy(app)

app.config['SESSION_SQLALCHEMY'] = session_db

sess = Session(app)

session_db.create_all()

socketio = SocketIO(app, manage_session=False)

CURRENT_DIRECTORY = (os.path.realpath(__file__)).replace(os.path.basename(__file__), "")
DATABASE_DIRECTORIES = "uploaded_databases"

_db_uri = "sqlite:///"
_base = declarative_base()
_engine = None
_session = None
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
    return session["client_uuid"]

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
        databases_dir = os.path.join(CURRENT_DIRECTORY + DATABASE_DIRECTORIES + "/")
        print("database dir : " + str(databases_dir))
        if not os.path.isdir(databases_dir):
            os.mkdir(databases_dir)

        user_dict = {"db_name": str(uuid.uuid4())}
        session["user_dict"] = user_dict
        session["sa_session"] = _session
        data.save(os.path.join(databases_dir, user_dict["db_name"]))
        print("data saved")

        def ack_db_pwd(password):
            print(password)
            # TODO: decrypt db
        socketio.emit("request_pwd", room=session["client_uuid"], callback=lambda x: print(str(x)))
        return "1"

        global _db_uri
        _db_uri += databases_dir + "/" + data.filename

        #TODO: socketIo database loaded
        #global _session
        #_session = initDbInstance()

        #TODO: socketIo validating database
        _settings = load_settings(_session)

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
    return render_template('index.html', client_uuid=(session["client_uuid"] if "client_uuid" in session else None))

if __name__ == "__main__":
    socketio.run(app=app, port=13226)

