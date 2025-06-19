#! /usr/bin/env python3

from flask import Flask
from db import close_connection
from routes import register_blueprints

app = Flask(__name__)
register_blueprints(app)

@app.teardown_appcontext
def teardown_db(exception):
    close_connection(exception)

@app.route('/')
def hello_world():
    return 'Hello World from Raspberry Pi 4!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)