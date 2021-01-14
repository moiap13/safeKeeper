#!/usr/bin/env python3
import os
import sys
from flask import Flask, render_template, request, make_response, jsonify
from sqlalchemy import Column, String, BLOB, Integer, create_engine, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_socketio import SocketIO, send, emit

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/terminal")

import main


app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app)

CURRENT_DIRECTORY = (os.path.realpath(__file__)).replace(os.path.basename(__file__), "")
DATABASE_DIRECTORIES = "uploaded_databases"

_db_uri = "sqlite:///"
_base = declarative_base()
_engine = None
_session = None
_password = None

def initDbInstance():
    global _engine
    _engine = create_engine(_db_uri, echo=False)
    _session = sessionmaker(bind=_engine)
    return _session()

def load_settings(session):
    s = session.query(main.Settings).all()
    return s[0]

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connection')
def another_event(data):
    print(data)

@app.route("/droppedfiles", methods=["POST"])
def droppedfiles():
    if request.files:
        data = request.files["databasefile"]
        databases_dir = os.path.join(CURRENT_DIRECTORY + DATABASE_DIRECTORIES + "/")
        print("database dir : " + str(databases_dir))
        if not os.path.isdir(databases_dir):
            os.mkdir(databases_dir)

        data.save(os.path.join(databases_dir, data.filename))
        print("data saved")
        socketio.emit("infos", "data saved")
        return "1"

        global _db_uri
        _db_uri += databases_dir + "/" + data.filename

        #TODO: socketIo database loaded
        global _session
        _session = initDbInstance()

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

if __name__ == "__main__":
    socketio.run(app=app, port=13226)

