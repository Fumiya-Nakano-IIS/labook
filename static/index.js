let currentSortKey = 'updatedtime';
let currentSortOrder = 'desc';
let filterStatus = false;

document.addEventListener('DOMContentLoaded', function () {


    const headers = Array.from(document.querySelectorAll('#booksTable thead th[data-key]'))
        .map(th => ({
            th,
            key: th.dataset.key,
            indicator: th.querySelector('.indicator')
        }));

    function renderIndicators() {
        headers.forEach(({ key, indicator }) => {
            indicator.innerHTML = '';
            if (key === 'status') {
                indicator.innerHTML = filterStatus
                    ? '<i class="fas fa-check-square" aria-hidden="true"></i>'
                    : '<i class="far fa-square" aria-hidden="true"></i>';
            }
            else if (currentSortKey === key) {
                indicator.innerHTML = currentSortOrder === 'asc'
                    ? '<i class="fas fa-arrow-up" aria-hidden="true"></i>'
                    : '<i class="fas fa-arrow-down" aria-hidden="true"></i>';
            } else {
                indicator.innerHTML = '<i class="fas fa-sort" aria-hidden="true" style="font-size: 0.75em;"></i>';
            }
        });
    }

    headers.forEach(({ th, key }) => {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => {
            if (key === 'status') {
                filterStatus = !filterStatus;
            } else {
                if (currentSortKey === key) {
                    currentSortOrder = currentSortOrder === 'asc' ? 'desc' : 'asc';
                    if (!currentSortOrder) currentSortKey = null;
                } else {
                    currentSortKey = key;
                    currentSortOrder = 'asc';
                }
            }

            renderIndicators();
            updateBooksTable();
        });
    });

    document.getElementById('searchInput').addEventListener('keydown', function (e) {
        if (e.key === 'Enter') updateBooksTable();
    });

    document.getElementById('searchBtn').addEventListener('click', function () {
        updateBooksTable();
    });
    document.getElementById('resetBtn').addEventListener('click', function () {
        document.getElementById('searchInput').value = '';
        currentSortKey = 'updatedtime';
        currentSortOrder = 'desc';
        filterStatus = false;
        renderIndicators();
        updateBooksTable();
    });
    document.getElementById('addBookBtn').addEventListener('click', function () {
        window.location.href = '/books/manage';
    });

    renderIndicators();
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
