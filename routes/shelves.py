from flask import Blueprint, request, jsonify, abort
from db import get_db

bp = Blueprint('shelves', __name__, url_prefix='/shelves')

@bp.route('', methods=['GET'])
def list_shelves():
    db = get_db()
    cursor = db.execute("SELECT * FROM Shelves")
    shelves = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    return jsonify(shelves)

@bp.route('/<code>', methods=['GET'])
def get_shelf(code):
    db = get_db()
    cursor = db.execute("SELECT * FROM Shelves WHERE shelf_code = ?", (code,))
    row = cursor.fetchone()
    if row is None:
        abort(404, description="Shelf not found")
    return jsonify(dict(zip([col[0] for col in cursor.description], row)))

@bp.route('', methods=['POST'])
def add_shelf():
    data = request.get_json()
    if 'shelf_code' not in data or 'shelf_name' not in data:
        abort(400, description="Missing required fields")
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Shelves (shelf_code, shelf_name, location_description) VALUES (?, ?, ?)",
            (data['shelf_code'], data['shelf_name'], data.get('location_description'))
        )
        db.commit()
    except Exception:
        abort(409, description="Shelf already exists")
    return jsonify({"message": "Shelf added"}), 201

@bp.route('/<code>', methods=['PUT'])
def update_shelf(code):
    data = request.get_json()
    db = get_db()
    cursor = db.execute("SELECT * FROM Shelves WHERE shelf_code = ?", (code,))
    if cursor.fetchone() is None:
        abort(404, description="Shelf not found")
    db.execute(
        "UPDATE Shelves SET shelf_name=?, location_description=? WHERE shelf_code=?",
        (data.get('shelf_name'), data.get('location_description'), code)
    )
    db.commit()
    return jsonify({"message": "Shelf updated"})

@bp.route('/<code>', methods=['DELETE'])
def delete_shelf(code):
    db = get_db()
    cursor = db.execute("SELECT * FROM Shelves WHERE shelf_code = ?", (code,))
    if cursor.fetchone() is None:
        abort(404, description="Shelf not found")
    db.execute("DELETE FROM Shelves WHERE shelf_code = ?", (code,))
    db.commit()
    return jsonify({"message": "Shelf deleted"})