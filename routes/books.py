from flask import Blueprint, request, jsonify, abort
from db import get_db

bp = Blueprint('books', __name__, url_prefix='/books')

@bp.route('', methods=['GET'])
def list_books():
    db = get_db()
    cursor = db.execute("SELECT * FROM Books")
    books = [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]
    return jsonify(books)

@bp.route('/<isbn>', methods=['GET'])
def get_book(isbn):
    db = get_db()
    cursor = db.execute("SELECT * FROM Books WHERE isbn = ?", (isbn,))
    row = cursor.fetchone()
    if row is None:
        abort(404, description="Book not found")
    return jsonify(dict(zip([col[0] for col in cursor.description], row)))

@bp.route('', methods=['POST'])
def add_book():
    data = request.get_json()
    required = ['isbn', 'title']
    if not all(k in data for k in required):
        abort(400, description="Missing required fields")
    db = get_db()
    try:
        db.execute(
            "INSERT INTO Books (isbn, title, author, publisher, publication_date, cover_image_path, owner_id, comment, shelf_code) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data['isbn'], data['title'], data.get('author'), data.get('publisher'),
                data.get('publication_date'), data.get('cover_image_path'), data.get('owner_id'),
                data.get('comment'), data.get('shelf_code')
            )
        )
        db.commit()
    except Exception:
        abort(409, description="Book with this ISBN already exists")
    return jsonify({"message": "Book added"}), 201

@bp.route('/<isbn>', methods=['PUT'])
def update_book(isbn):
    data = request.get_json()
    db = get_db()
    cursor = db.execute("SELECT * FROM Books WHERE isbn = ?", (isbn,))
    if cursor.fetchone() is None:
        abort(404, description="Book not found")
    db.execute(
        """UPDATE Books SET title=?, author=?, publisher=?, publication_date=?, cover_image_path=?, owner_id=?, comment=?, shelf_code=?
           WHERE isbn=?""",
        (
            data.get('title'), data.get('author'), data.get('publisher'),
            data.get('publication_date'), data.get('cover_image_path'), data.get('owner_id'),
            data.get('comment'), data.get('shelf_code'), isbn
        )
    )
    db.commit()
    return jsonify({"message": "Book updated"})

@bp.route('/<isbn>', methods=['DELETE'])
def delete_book(isbn):
    db = get_db()
    cursor = db.execute("SELECT * FROM Books WHERE isbn = ?", (isbn,))
    if cursor.fetchone() is None:
        abort(404, description="Book not found")
    db.execute("DELETE FROM Books WHERE isbn = ?", (isbn,))
    db.commit()
    return jsonify({"message": "Book deleted"})