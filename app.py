#! /usr/bin/env python3

from flask import Flask, send_from_directory,render_template
from db import close_connection,init_db,dbname
from routes import register_blueprints
import os

app = Flask(__name__)
register_blueprints(app)

@app.teardown_appcontext
def teardown_db(exception):
    close_connection(exception)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/backup')
def backup():
    if os.path.exists(dbname):
        import datetime, shutil
        backup_file = dbname + datetime.datetime.now().strftime("_%Y%m%d-%H%M%S") + '.db'
        shutil.copy(dbname, backup_file)
        return f"Backup created: {backup_file}"
    else:
        return "Database file does not exist."

@app.route('/initdb')
def initdb():
    if app.debug:
        backup()
        init_db()
        return "Database initialized!"
    else:
        return "Database initialization is only allowed in debug mode."

@app.route('/covers/<filename>')
def serve_cover(filename):
    covers_dir = 'covers'
    return send_from_directory(covers_dir, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)