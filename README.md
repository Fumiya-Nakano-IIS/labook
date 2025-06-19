# Labook Database

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
| `affiliation` | TEXT    |                           | Lab or department  |

---

### `Loans`

| Column        | Type    | Constraints                   | Description                         |
| ------------- | ------- | ----------------------------- | ----------------------------------- |
| `loan_id`     | INTEGER | PRIMARY KEY AUTOINCREMENT     | Loan record ID                      |
| `isbn`        | TEXT    | FOREIGN KEY → `Books.isbn`    | ISBN of the borrowed book           |
| `user_id`     | INTEGER | FOREIGN KEY → `Users.user_id` | Borrowing user                      |
| `loan_date`   | TEXT    | NOT NULL                      | Checkout date                       |
| `due_date`    | TEXT    |                               | Expected return date (user input)   |
| `return_date` | TEXT    |                               | Actual return date (NULL = not yet) |

---

## 📡 REST API Design

Below are the RESTful API endpoints for managing books, shelves, users, and loans.

### 📚 Books

| Method | Endpoint           | Description                  |
|--------|--------------------|------------------------------|
| GET    | `/books`           | List all books               |
| GET    | `/books/<isbn>`    | Get details for a book       |
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
  "shelf_code": "A1"
}
```

---

### 🗄️ Shelves

| Method | Endpoint             | Description                  |
|--------|----------------------|------------------------------|
| GET    | `/shelves`           | List all shelves             |
| GET    | `/shelves/<code>`    | Get shelf details            |
| POST   | `/shelves`           | Add a new shelf              |
| PUT    | `/shelves/<code>`    | Update shelf info            |
| DELETE | `/shelves/<code>`    | Delete a shelf               |

---

### 👤 Users

| Method | Endpoint           | Description                  |
|--------|--------------------|------------------------------|
| GET    | `/users`           | List all users               |
| GET    | `/users/<id>`      | Get user details             |
| POST   | `/users`           | Add a new user               |
| PUT    | `/users/<id>`      | Update user info             |
| DELETE | `/users/<id>`      | Delete a user                |

---

### 🔄 Loans

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

### 📖 Book Status

- To get current status (on shelf/on loan), use `/books` or `/books/<isbn>` and include status in the response, using the SQL below.

---

## 🔍 How to Determine Current Book Status

- A book is **"on shelf"** if there is no loan record with `return_date IS NULL`.
- A book is **"on loan"** if there exists a `Loans` record for that ISBN with `return_date IS NULL`.

Example SQL:

```sql
-- Check current loan status
SELECT
  B.isbn,
  B.title,
  S.shelf_name,
  U.name AS current_holder,
  CASE
    WHEN L.return_date IS NULL THEN 'On Loan'
    ELSE 'On Shelf'
  END AS status
FROM Books B
LEFT JOIN Shelves S ON B.shelf_code = S.shelf_code
LEFT JOIN Loans L ON B.isbn = L.isbn AND L.return_date IS NULL
LEFT JOIN Users U ON L.user_id = U.user_id;
```

## 📌 Notes

- Each book has one owner (owner_id), which is a lab member (Users table).
- Comments allow optional remarks (e.g., damage, language, edition).
- Lending records are not restricted by copy (still one record per ISBN).
- Cover images are managed via path (e.g. /covers/9781234567890.jpg).