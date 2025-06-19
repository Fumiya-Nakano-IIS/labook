#! /usr/bin/env python3

from flask import Flask, g, request, redirect, url_for
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
    return 'Hello World from Raspberry Pi 4!'

@app.route('/books')
def list_books():
    db = get_db()
    cursor = db.execute("SELECT id, title, author FROM books")
    books = cursor.fetchall()
    # Format as simple HTML list
    html = "<h1>Books</h1><ul>"
    for book in books:
        html += f"<li>{book[1]} by {book[2]} (ID: {book[0]})</li>"
    html += "</ul>"
    return html

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        db = get_db()
        db.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        db.commit()
        return redirect(url_for('list_books'))
    # Show form
    return '''
        <h1>Add Book</h1>
        <form method="post">
            Title: <input type="text" name="title"><br>
            Author: <input type="text" name="author"><br>
            <input type="submit" value="Add Book">
        </form>
        <a href="/books">Back to book list</a>
    '''


if __name__ == '__main__':
    # Listen on all interfaces, port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)