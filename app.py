#! /usr/bin/env python3

from flask import Flask, send_from_directory
from db import close_connection
from routes import register_blueprints
import os

app = Flask(__name__)
register_blueprints(app)

@app.teardown_appcontext
def teardown_db(exception):
    close_connection(exception)

@app.route('/')
def hello_world():
    return 'Hello World from Raspberry Pi 4!'

@app.route('/initdb')
def init_db():
    from db import get_db
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        affiliation TEXT
    );
    CREATE TABLE IF NOT EXISTS Shelves (
        shelf_code TEXT PRIMARY KEY,
        shelf_name TEXT NOT NULL,
        location_description TEXT
    );
    CREATE TABLE IF NOT EXISTS Books (
        isbn TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT,
        publisher TEXT,
        publication_date TEXT,
        cover_image_path TEXT,
        owner_id INTEGER,
        comment TEXT,
        shelf_code TEXT,
        FOREIGN KEY(owner_id) REFERENCES Users(user_id),
        FOREIGN KEY(shelf_code) REFERENCES Shelves(shelf_code)
    );
    CREATE TABLE IF NOT EXISTS Loans (
        loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        isbn TEXT,
        user_id INTEGER,
        loan_date TEXT NOT NULL,
        due_date TEXT,
        return_date TEXT,
        FOREIGN KEY(isbn) REFERENCES Books(isbn),
        FOREIGN KEY(user_id) REFERENCES Users(user_id)
    );
    """)
    db.commit()
    return "Database initialized!"

@app.route('/covers/<filename>')
def serve_cover(filename):
    covers_dir = 'covers'
    return send_from_directory(covers_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)