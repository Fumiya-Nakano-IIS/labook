# laBook

This schema manages lab library books, their owners, and current lending status.

---

## 📚 Tables

### `Books`

| Column             | Type    | Constraints                        | Description                   |
| ------------------ | ------- | ---------------------------------- | ----------------------------- |
| `isbn`             | TEXT    | PRIMARY KEY                        | ISBN of the book (unique key) |
| `title`            | TEXT    | NOT NULL                           | Title of the book             |
| `author`           | TEXT    |                                    | Author(s)                     |
| `publisher`        | TEXT    |                                    | Publisher                     |
| `publication_date` | TEXT    |                                    | Publication date              |
| `cover_image_path` | TEXT    |                                    | Path to cover image           |
| `owner_id`         | INTEGER | FOREIGN KEY → `Users.user_id`      | Owner of the book             |
| `comment`          | TEXT    |                                    | Free-text memo for notes      |
| `shelf_code`       | TEXT    | FOREIGN KEY → `Shelves.shelf_code` | Home shelf (default location) |

---

### `Shelves`

| Column                 | Type | Constraints | Description                |
| ---------------------- | ---- | ----------- | -------------------------- |
| `shelf_code`           | TEXT | PRIMARY KEY | Unique shelf ID (e.g., A1) |
| `shelf_name`           | TEXT | NOT NULL    | Display name of the shelf  |
| `location_description` | TEXT |             | Additional description     |

---

### `Users`

| Column        | Type    | Constraints               | Description        |
| ------------- | ------- | ------------------------- | ------------------ |
| `user_id`     | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique internal ID |
| `name`        | TEXT    | NOT NULL                  | User's name        |
| `email`       | TEXT    |                           | Email address      |

---

### `Loans`

| Column        | Type    | Constraints               | Description           |
| ------------- | ------- | ------------------------- | --------------------- |
| `loan_id`     | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique loan ID        |
| `isbn`        | TEXT    | FOREIGN KEY → Books.isbn  | Loaned book           |
| `user_id`     | INTEGER | FOREIGN KEY → Users.user_id | Borrower             |
| `loan_date`   | TEXT    | NOT NULL                  | Date loaned out       |
| `due_date`    | TEXT    |                           | Due date (optional)   |
| `return_date` | TEXT    |                           | Date returned (NULL if not returned) |

---

- Cover images are managed via path (e.g. /covers/9781234567890.jpg).

---

## 📡 REST API

The backend is implemented in Flask with endpoints grouped by resource.  
All endpoints return and accept JSON.

### Books

| Method | Endpoint           | Description                  |
|--------|--------------------|------------------------------|
| GET    | `/books`           | List all books (with status) |
| GET    | `/books/<isbn>`    | Get details for a book (with status) |
| POST   | `/books`           | Add a new book               |
| PUT    | `/books/<isbn>`    | Update book info             |
| DELETE | `/books/<isbn>`    | Delete a book                |

**Book JSON Example:**
```json
{
  "isbn": "9781234567890",
  "title": "Book Title",
  "author": "Author Name",
  "publisher": "Publisher",
  "publication_date": "2020-01-01",
  "cover_image_path": "/covers/9781234567890.jpg",
  "owner_id": 1,
  "comment": "Some notes",
  "shelf_code": "A1",
  "status": "On Shelf" // or "On Loan"
}
```

**Book Status:**  
- The `status` field is `"On Loan"` if there is a loan record for the book with `return_date` as NULL, otherwise `"On Shelf"`.

---

### Shelves

| Method | Endpoint             | Description                  |
|--------|----------------------|------------------------------|
| GET    | `/shelves`           | List all shelves             |
| GET    | `/shelves/<code>`    | Get shelf details            |
| POST   | `/shelves`           | Add a new shelf              |
| PUT    | `/shelves/<code>`    | Update shelf info            |
| DELETE | `/shelves/<code>`    | Delete a shelf               |

---

### Users

| Method | Endpoint           | Description                  |
|--------|--------------------|------------------------------|
| GET    | `/users`           | List all users               |
| GET    | `/users/<id>`      | Get user details             |
| POST   | `/users`           | Add a new user               |
| PUT    | `/users/<id>`      | Update user info             |
| DELETE | `/users/<id>`      | Delete a user                |

---

### Loans

| Method | Endpoint           | Description                       |
|--------|--------------------|-----------------------------------|
| GET    | `/loans`           | List all loans                    |
| GET    | `/loans/<id>`      | Get loan details                  |
| POST   | `/loans`           | Create a new loan (checkout book) |
| PUT    | `/loans/<id>`      | Update loan (e.g., return book)   |
| DELETE | `/loans/<id>`      | Delete a loan record              |

**Loan JSON Example:**
```json
{
  "isbn": "9781234567890",
  "user_id": 2,
  "loan_date": "2024-06-19",
  "due_date": "2024-07-19",
  "return_date": null
}
```

---

## 📦 Project Structure

```
labook/
├── app.py
├── db.py
├── routes/
│   ├── __init__.py
│   ├── books.py
│   ├── shelves.py
│   ├── users.py
│   └── loans.py
├── library.db
├── README.md
```

---

## 🛠️ How Book Status is Determined

For each book, status is determined by:

```sql
SELECT 1 FROM Loans WHERE isbn = ? AND return_date IS NULL LIMIT 1
```
- If a row exists, status is `"On Loan"`.
- Otherwise, status is `"On Shelf"`.

---

## 🏁 Quickstart

1. Install dependencies:  
   `pip install flask`
2. Run the app:  
   `python app.py`
3. Use the API endpoints as described