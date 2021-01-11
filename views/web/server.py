#!/usr/bin/env python3
import os
import sys
from flask import Flask, render_template, request, make_response, jsonify

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/droppedfiles", methods=["POST"])
def droppedfiles():
    if request.files:
        data = request.files["databasefile"]

        #data.save(os.path.join("/home/antonio/Documents/antonio/develepement/python/safeKeeper", data.filename))

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
    app.run(port=13226)
