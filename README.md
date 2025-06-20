# laBook

このプロジェクトは、研究室の蔵書管理・貸出管理を行うWebアプリです。

---

## 📚 テーブル構成

### `Books`

| カラム名           | 型      | 制約                               | 説明                   |
| ------------------ | ------- | ---------------------------------- | ---------------------- |
| `isbn`             | TEXT    | PRIMARY KEY                        | 書籍のISBN（ユニーク） |
| `title`            | TEXT    | NOT NULL                           | 書名                   |
| `author`           | TEXT    |                                    | 著者                   |
| `publisher`        | TEXT    |                                    | 出版社                 |
| `publication_date` | TEXT    |                                    | 出版日                 |
| `cover_image_path` | TEXT    |                                    | 表紙画像パス           |
| `owner_id`         | INTEGER | FOREIGN KEY → `Users.user_id`      | 所有者                 |
| `comment`          | TEXT    |                                    | メモ                   |
| `shelf_code`       | TEXT    | FOREIGN KEY → `Shelves.shelf_code` | 所蔵棚                 |

---

### `Shelves`

| カラム名               | 型   | 制約        | 説明           |
| ---------------------- | ---- | ----------- | -------------- |
| `shelf_code`           | TEXT | PRIMARY KEY | 棚ID（例: A1） |
| `shelf_name`           | TEXT | NOT NULL    | 棚の表示名     |
| `location_description` | TEXT |             | 棚の説明       |

---

### `Users`

| カラム名  | 型      | 制約                      | 説明           |
| --------- | ------- | ------------------------- | -------------- |
| `user_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | ユーザーID     |
| `name`    | TEXT    | NOT NULL                  | 氏名           |
| `email`   | TEXT    |                           | メールアドレス |

---

### `Loans`

| カラム名      | 型      | 制約                        | 説明                   |
| ------------- | ------- | --------------------------- | ---------------------- |
| `loan_id`     | INTEGER | PRIMARY KEY AUTOINCREMENT   | 貸出ID                 |
| `isbn`        | TEXT    | FOREIGN KEY → Books.isbn    | 貸出書籍               |
| `borrower_id` | INTEGER | FOREIGN KEY → Users.user_id | 借主                   |
| `returner_id` | INTEGER | FOREIGN KEY → Users.user_id | 返却者                 |
| `loan_date`   | TEXT    | NOT NULL                    | 貸出日                 |
| `due_date`    | TEXT    |                             | 返却期限               |
| `return_date` | TEXT    |                             | 返却日（未返却はNULL） |

---

## 📡 REST API

Flaskで実装。全てJSONでやりとりします。

### Books

| Method | Endpoint                            | 説明                                |
| ------ | ----------------------------------- | ----------------------------------- |
| GET    | `/books`                            | 全書籍一覧（ステータス付き）        |
| GET    | `/books/<isbn>`                     | 書籍詳細（ステータス付き）          |
| POST   | `/books`                            | 書籍追加                            |
| PUT    | `/books/<isbn>`                     | 書籍情報更新                        |
| DELETE | `/books/<isbn>`                     | 書籍削除                            |
| GET    | `/books/api/fetch_book_info/<isbn>` | ISBNから書誌情報取得（外部API連携） |

**Book JSON例:**
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
  "status": "On Shelf" // または "On Loan"
}
```

- `status`は貸出中なら"On Loan"、そうでなければ"On Shelf"。

---

### Shelves

| Method | Endpoint          | 説明       |
| ------ | ----------------- | ---------- |
| GET    | `/shelves`        | 棚一覧     |
| GET    | `/shelves/<code>` | 棚詳細     |
| POST   | `/shelves`        | 棚追加     |
| PUT    | `/shelves/<code>` | 棚情報更新 |
| DELETE | `/shelves/<code>` | 棚削除     |

---

### Users

| Method | Endpoint      | 説明             |
| ------ | ------------- | ---------------- |
| GET    | `/users`      | ユーザー一覧     |
| GET    | `/users/<id>` | ユーザー詳細     |
| POST   | `/users`      | ユーザー追加     |
| PUT    | `/users/<id>` | ユーザー情報更新 |
| DELETE | `/users/<id>` | ユーザー削除     |

---

### Loans

| Method | Endpoint      | 説明                     |
| ------ | ------------- | ------------------------ |
| GET    | `/loans`      | 貸出一覧                 |
| GET    | `/loans/<id>` | 貸出詳細                 |
| POST   | `/loans`      | 新規貸出                 |
| PUT    | `/loans/<id>` | 貸出情報更新（返却など） |
| DELETE | `/loans/<id>` | 貸出記録削除             |

**Loan JSON例:**
```json
{
  "isbn": "9781234567890",
  "borrower_id": 2,
  "returner_id": 3,
  "loan_date": "2024-06-19",
  "due_date": "2024-07-19",
  "return_date": null
}
```

---

## 📖 書籍追加・編集ページ

- `/books/manage` でISBNを入力すると、  
  - DBに存在すれば編集フォーム
  - 存在しなければ外部APIから自動取得して追加フォーム
- 1ページで追加・編集どちらも対応
- ISBN入力時に自動判定・自動取得

---

## 📦 ディレクトリ構成例

```
labook/
├── app.py
├── db.py
├── fetch_book_info.py
├── routes/
│   ├── __init__.py
│   ├── books.py
│   ├── shelves.py
│   ├── users.py
│   └── loans.py
├── static/
│   └── book_form.js
├── templates/
│   └── manage_book.html
├── library.db
├── README.md
```

---

## 🏁 クイックスタート

1. 依存インストール  
   `pip install flask requests`
2. DB初期化  
   `/initdb` にアクセス
3. サーバ起動  
   `python app.py`
4. `/books/manage` で書籍追加・編集