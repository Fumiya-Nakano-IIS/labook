from flask import Blueprint, request, jsonify, abort, render_template, redirect, url_for
from db import get_db
import fetch_book_info
import requests
import logging

bp = Blueprint('books', __name__, url_prefix='/books')
logger = logging.getLogger(__name__)

def get_book_status(db, isbn):
    cursor = db.execute(
        "SELECT 1 FROM Loans WHERE isbn = ? AND return_date IS NULL LIMIT 1", (isbn,)
    )
    if cursor.fetchone() is None:
        return None
    else:   
        user = db.execute(
            "SELECT borrower_id FROM Loans WHERE isbn = ? AND return_date IS NULL LIMIT 1", (isbn,)
        ).fetchone()
        if user:
            user_id = user[0]
            cursor = db.execute("SELECT name FROM Users WHERE user_id = ?", (user_id,))
            borrower = cursor.fetchone()
            if borrower:
                return f"{borrower[0]}"
        else:            
            return "Error: No borrower found"

def get_or_create_shelf_id(shelf_code, shelf_name=None, location_description=None):
    from flask import current_app
    api_url = f"http://localhost:5000/shelves/by_code/{shelf_code}"
    try:
        resp = requests.get(api_url)
        if resp.status_code == 200:
            return resp.json()['shelf_id']
    except Exception:
        pass
    api_url = f"http://localhost:5000/shelves"
    payload = {
        "shelf_code": shelf_code,
        "shelf_name": shelf_name or shelf_code,
        "location_description": location_description or ""
    }
    resp = requests.post(api_url, json=payload)
    if resp.status_code in (200, 201):
        return resp.json()['shelf_id']
    else:
        raise Exception("Failed to create shelf")

@bp.route('', methods=['GET'])
def list_books():
    db = get_db()
    sort_key = request.args.get('sort', 'updatedtime') 
    order = request.args.get('order', 'desc')     
    offset = request.args.get('offset', type=int, default=0)
    limit = request.args.get('limit', type=int, default=100)
    keyword = request.args.get('keyword', '').strip()

    valid_sort_keys = {'isbn', 'title', 'author', 'publisher', 'publication_date', 'updatedtime', 'shelf_id'}
    if sort_key not in valid_sort_keys:
        sort_key = 'title'
    if order not in {'asc', 'desc'}:
        order = 'asc'

    sql = """
    SELECT * FROM Books
    """
    params = []
    if keyword:
        if keyword.startswith('shelf_id:'):
            sql += " WHERE shelf_id = ? "
            params.append(keyword.split(':', 1)[1])
        else:
            sql += " WHERE title LIKE ? OR author LIKE ? OR publisher LIKE ? OR isbn LIKE ? "
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw, keyword])
    sql += f" ORDER BY {sort_key} {order.upper()} LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    cursor = db.execute(sql, params)
    books = []
    columns = [col[0] for col in cursor.description]
    for row in cursor.fetchall():
        book = dict(zip(columns, row))
        book['status'] = get_book_status(db, book['isbn'])
        books.append(book)
    return jsonify(books)

@bp.route('/<isbn>', methods=['GET'])
def get_book(isbn):
    db = get_db()
    cursor = db.execute("SELECT * FROM Books WHERE isbn = ?", (isbn,))
    row = cursor.fetchone()
    if row is None:
        abort(404, description="Book not found")
    book = dict(zip([col[0] for col in cursor.description], row))
    book['status'] = get_book_status(db, isbn)
    return jsonify(book)

@bp.route('', methods=['POST'])
def add_book():
    data = request.get_json()
    required = ['isbn', 'title']
    if not all(k in data for k in required):
        abort(400, description="Missing required fields")
    db = get_db()
    shelf_id = data.get('shelf_id')
    if not shelf_id and data.get('shelf_code'):
        shelf_id = get_or_create_shelf_id(
            data['shelf_code'],
            data.get('shelf_name'),
            data.get('location_description')
        )
    try:
        db.execute(
            "INSERT INTO Books (isbn, title, author, publisher, publication_date, cover_image_path, owner_id, comment, shelf_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data['isbn'], data['title'], data.get('author'), data.get('publisher'),
                data.get('publication_date'), data.get('cover_image_path'), data.get('owner_id'),
                data.get('comment'), shelf_id
            )
        )
        db.commit()
        logger.info(f"Book added: {data}")
    except Exception:
        abort(409, description=Exception)
        logger.error(f"Failed to add book: {data}")
    return jsonify({"message": "Book added"}), 201

@bp.route('/<isbn>', methods=['PUT'])
def update_book(isbn):
    data = request.get_json()
    db = get_db()
    cursor = db.execute("SELECT * FROM Books WHERE isbn = ?", (isbn,))
    if cursor.fetchone() is None:
        abort(404, description="Book not found")
    shelf_id = data.get('shelf_id')
    if not shelf_id and data.get('shelf_code'):
        shelf_id = get_or_create_shelf_id(
            data['shelf_code'],
            data.get('shelf_name'),
            data.get('location_description')
        )
    db.execute(
        """UPDATE Books SET title=?, author=?, publisher=?, publication_date=?, cover_image_path=?, owner_id=?, comment=?, shelf_id=?
           WHERE isbn=?""",
        (
            data.get('title'), data.get('author'), data.get('publisher'),
            data.get('publication_date'), data.get('cover_image_path'), data.get('owner_id'),
            data.get('comment'), shelf_id, isbn
        )
    )
    db.commit()
    logger.info(f"Book updated: {data}")
    return jsonify({"message": "Book updated"})

@bp.route('/<isbn>', methods=['DELETE'])
def delete_book(isbn):
    db = get_db()
    cursor = db.execute("SELECT * FROM Books WHERE isbn = ?", (isbn,))
    if cursor.fetchone() is None:
        abort(404, description="Book not found")
    db.execute("DELETE FROM Books WHERE isbn = ?", (isbn,))
    db.commit()
    logger.info(f"Book deleted: {isbn}")
    return jsonify({"message": "Book deleted"})

@bp.route('/api/fetch_book_info/<isbn>')
def api_fetch_book_info(isbn):
    info = fetch_book_info.fetch_book_info(isbn)
    if info:
        return jsonify(info)
    else:
        return jsonify({"error": "No book info found"}), 404

@bp.route('/manage', methods=['GET', 'POST'])
def manage_book_page():
    import requests
    from flask import current_app

    error = None
    book = None
    mode = "add"
    isbn = request.args.get('isbn') or (request.form.get('isbn') if request.method == 'POST' else None)
    keep_owner_id = ""
    keep_shelf_code = ""

    if isbn:
        resp = requests.get(f"http://localhost:5000/books/{isbn}")
        if resp.status_code == 200:
            book = resp.json()
            mode = "edit"
        else:
            import fetch_book_info
            info = fetch_book_info.fetch_book_info(isbn)
            if info:
                book = info
            else:
                book = {"isbn": isbn}

    if request.method == 'POST':
        data = request.form.to_dict()
        keep_owner_id = data.get('owner_id', '')
        keep_shelf_code = data.get('shelf_code', '')

        shelf_id = None
        if data.get('shelf_code'):
            shelf_resp = requests.get(f"http://localhost:5000/shelves/by_code/{data['shelf_code']}")
            if shelf_resp.ok:
                shelf_id = shelf_resp.json()['shelf_id']
            else:
                create_resp = requests.post(
                    "http://localhost:5000/shelves",
                    json={
                        "shelf_code": data['shelf_code'],
                        "location_description": ""
                    }
                )
                if create_resp.ok:
                    shelf_id = create_resp.json()['shelf_id']
                else:
                    error = "failed to make shelf"
        data['shelf_id'] = shelf_id

        if mode == "edit":
            resp = requests.put(
                f"http://localhost:5000/books/{isbn}",
                json={**data, "isbn": isbn, "shelf_id": shelf_id}
            )
        else:
            resp = requests.post(
                "http://localhost:5000/books",
                json={**data, "isbn": isbn, "shelf_id": shelf_id}
            )
        if resp.ok:
            return redirect(url_for('books.manage_book_page', isbn=isbn))
        else:
            error = resp.json().get('description', 'failed to book register')

    if book and book.get('shelf_id'):
        shelf_resp = requests.get(f"http://localhost:5000/shelves/{book['shelf_id']}")
        if shelf_resp.ok:
            shelf = shelf_resp.json()
            book['shelf_code'] = shelf.get('shelf_code', '')
        else:
            book['shelf_code'] = ""
    if mode == "add" and (keep_owner_id or keep_shelf_code):
        if not book:
            book = {}
        book['owner_id'] = keep_owner_id
        book['shelf_code'] = keep_shelf_code

    return render_template('manage_book.html', book=book, error=error, mode=mode)