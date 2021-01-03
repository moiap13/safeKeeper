#!/usr/bin/env python3
import os
import sys
from flask import Flask, render_template

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, template_folder="templates")

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(port=13226)
