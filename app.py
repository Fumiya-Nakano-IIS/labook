#! /usr/bin/env python3

from flask import Flask, g
import sqlite3
import os

app = Flask(__name__)
# Path to SQLite database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'library.db')

# Helper to get or create the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Close DB connection on teardown
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Route: Hello World
@app.route('/')
def hello_world():
    return 'Hello, World from Raspberry Pi 4!'

if __name__ == '__main__':
    # Listen on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)