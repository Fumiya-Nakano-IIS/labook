let currentSortKey = 'updatedtime';
let currentSortOrder = 'desc';
let filterStatus = false;

document.addEventListener('DOMContentLoaded', function () {

    document.querySelectorAll('#booksTable thead th').forEach((th, idx) => {
        const keyMap = ['cover_image_path', 'title', 'author', 'publisher', 'publication_date', 'shelf_code', 'status'];
        if (idx === 0 || idx === 5) return;
        if (idx === 6) {
            th.style.cursor = 'pointer';
            th.addEventListener('click', function () {
                filterStatus = !filterStatus;
                th.textContent = th.textContent.slice(0, th.textContent.length - 2) + (filterStatus ? ' ■' : ' □');
                updateBooksTable();
            });
        } else {
            th.style.cursor = 'pointer';
            th.addEventListener('click', function () {
                const sortKey = keyMap[idx];
                if (sortKey === 'status') return;
                if (currentSortKey === sortKey) {
                    currentSortOrder = (currentSortOrder === 'asc') ? 'desc' : 'asc';
                } else {
                    currentSortKey = sortKey;
                    currentSortOrder = 'asc';
                }
                document.querySelectorAll('#booksTable thead th').forEach((th2, i2) => {
                    th2.textContent = th2.textContent.replace(' ▼', ' ▽').replace(' ▲', ' △');
                    if (i2 === idx) {
                        th2.textContent = th2.textContent.replace(' ▽', '').replace(' △', '') + (currentSortOrder === 'asc' ? ' ▲' : ' ▼');
                    }
                });
                updateBooksTable();
            });
        }
    });

    document.getElementById('searchBtn').addEventListener('click', function () {
        updateBooksTable();
    });
    document.getElementById('resetBtn').addEventListener('click', function () {
        document.getElementById('searchInput').value = '';
        updateBooksTable();
    });

    document.getElementById('searchInput').addEventListener('keydown', function (e) {
        if (e.key === 'Enter') updateBooksTable();
    });

    updateBooksTable();
});

async function updateBooksTable(sortKey = currentSortKey, sortOrder = currentSortOrder) {
    const tableBody = document.querySelector('#booksTable tbody');
    const keyword = document.getElementById('searchInput').value.trim();
    const statusOnly = filterStatus;
    let url = `/books?sort=${sortKey}&order=${sortOrder}&limit=100`;
    if (keyword) url += `&keyword=${encodeURIComponent(keyword)}`;
    try {
        const resp = await fetch(url);
        let books = await resp.json();
        if (statusOnly) {
            books = books.filter(book => book.status !== null && book.status !== undefined && book.status !== "");
        }
        tableBody.innerHTML = '';
        for (const book of books) {
            const tr = document.createElement('tr');
            let bookShelfCode = '';
            if (book.shelf_id) {
                try {
                    const shelfResp = await fetch(`/shelves/${book.shelf_id}`);
                    if (shelfResp.ok) {
                        const shelfData = await shelfResp.json();
                        bookShelfCode = shelfData.shelf_code || '';
                    }
                } catch (err) {
                    bookShelfCode = '';
                }
            }
            tr.innerHTML = `
                <td class="clickable-cover" style="cursor:pointer;">
                    <img src="${book.cover_image_path || ''}" alt="Cover Image" style="max-width: 60px; max-height: 100px;" />
                </td>
                <td class="clickable-title" style="cursor:pointer;"><a class='book-title'>${book.title || ''}</a></td>
                <td class="searchable-author" style="cursor:pointer">${book.author || ''}</td>
                <td class="searchable-publisher" style="cursor:pointer">${book.publisher || ''}</td>
                <td class="searchable-publication-date" style="cursor:pointer">${book.publication_date || ''}</td>
                <td class="searchable-shelf" style="cursor:pointer">${bookShelfCode || ''}</td>
                ${book.status ? `<td class="searchable-borrower" style="cursor:pointer">${book.borrower_id}</td>` : `<td>Available</td>`}
            `;
            tr.querySelector('.clickable-cover')?.addEventListener('click', function () {
                if (book.isbn) {
                    window.location.href = `/books/manage?isbn=${encodeURIComponent(book.isbn)}`;
                }
            });
            tr.querySelector('.clickable-title')?.addEventListener('click', function () {
                if (book.isbn) {
                    window.location.href = `/books/manage?isbn=${encodeURIComponent(book.isbn)}`;
                }
            });
            tr.querySelector('.searchable-author')?.addEventListener('click', function () {
                if (book.author) {
                    document.getElementById('searchInput').value = book.author;
                    updateBooksTable();
                }
            });
            tr.querySelector('.searchable-publisher')?.addEventListener('click', function () {
                if (book.publisher) {
                    document.getElementById('searchInput').value = book.publisher;
                    updateBooksTable();
                }
            });
            tr.querySelector('.searchable-shelf')?.addEventListener('click', function () {
                if (bookShelfCode) {
                    document.getElementById('searchInput').value = "shelf_id:" + String(book.shelf_id);
                    updateBooksTable();
                }
            });
            tr.querySelector('.clickable-status')?.addEventListener('click', function () {
                if (book.status) {
                    updateBooksTable();
                }
            });
            tableBody.appendChild(tr);
        }
        if (books.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7">No books found</td></tr>';
        }
    } catch (e) {
        tableBody.innerHTML = '<tr><td colspan="7">Failed to load books</td></tr>';
    }
}
