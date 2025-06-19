# Labook Database Schema (Revised)

This schema manages lab library books, their owners, and current lending status.

---

## 📚 Tables

### `Books`

| Column              | Type     | Constraints                  | Description                              |
|---------------------|----------|-------------------------------|------------------------------------------|
| `isbn`              | TEXT     | PRIMARY KEY                   | ISBN of the book (unique key)            |
| `title`             | TEXT     | NOT NULL                      | Title of the book                        |
| `author`            | TEXT     |                               | Author(s)                                |
| `publisher`         | TEXT     |                               | Publisher                                |
| `publication_date`  | TEXT     |                               | Publication date                         |
| `cover_image_path`  | TEXT     |                               | Path to cover image                      |
| `owner_id`          | INTEGER  | FOREIGN KEY → `Users.user_id` | Owner of the book                        |
| `comment`           | TEXT     |                               | Free-text memo for notes                 |
| `shelf_code`     | TEXT     |  FOREIGN KEY → `Shelves.shelf_code`     | Home shelf (default location)      |
---

### `Shelves`

| Column                | Type    | Constraints     | Description                       |
|------------------------|---------|------------------|-----------------------------------|
| `shelf_code`           | TEXT    | PRIMARY KEY      | Unique shelf ID (e.g., A1)        |
| `shelf_name`           | TEXT    | NOT NULL         | Display name of the shelf         |
| `location_description` | TEXT    |                  | Additional description            |

---

### `Users`

| Column        | Type     | Constraints             | Description                      |
|---------------|----------|--------------------------|----------------------------------|
| `user_id`     | INTEGER  | PRIMARY KEY AUTOINCREMENT| Unique internal ID               |
| `name`        | TEXT     | NOT NULL                 | User's name                      |
| `email`       | TEXT     |                          | Email address                    |
| `affiliation` | TEXT     |                          | Lab or department                |

---

### `Loans`

| Column        | Type     | Constraints                     | Description                                |
|----------------|----------|----------------------------------|--------------------------------------------|
| `loan_id`      | INTEGER  | PRIMARY KEY AUTOINCREMENT        | Loan record ID                             |
| `isbn`         | TEXT     | FOREIGN KEY → `Books.isbn`       | ISBN of the borrowed book                  |
| `user_id`      | INTEGER  | FOREIGN KEY → `Users.user_id`    | Borrowing user                             |
| `loan_date`    | TEXT     | NOT NULL                         | Checkout date                              |
| `due_date`     | TEXT     |                                  | Expected return date (user input)          |
| `return_date`  | TEXT     |                                  | Actual return date (NULL = not yet)        |

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