async function transferToEditPage(isbn) {
    const form = document.getElementById('manageBookForm');
    const mode = form.getAttribute('data-mode');
    if (mode !== 'edit' && await isBookExist(isbn)) {
        alert('Book already exists.\nRedirecting to manage page.');
        window.location.href = `/books/manage?isbn=${isbn}`;
        form.setAttribute('data-mode', 'edit');
        return true;
    }
    return false;
}

document.addEventListener('DOMContentLoaded', async function () {
    const isbnInput = document.getElementById('isbn');
    const form = document.getElementById('manageBookForm');
    const shelfCodeInput = document.getElementById('shelf_code');

    if (shelfCodeInput && shelfCodeInput.value && !isNaN(shelfCodeInput.value)) {

        try {
            const resp = await fetch(`/shelves/${shelfCodeInput.value}`);
            if (resp.ok) {
                const shelf = await resp.json();
                if (shelf.shelf_code) shelfCodeInput.value = shelf.shelf_code;
            }
        } catch (e) {
        }
    }

    if (!isbnInput || !form) {
        console.error('ISBN input or form not found');
        return;
    }

    isbnInput.addEventListener('change', async function () {
        fetchBookInfo();
    });

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const isbn = isbnInput.value;
        if (!isbnValidate(isbn)) {
            alert('Invalid ISBN.\nPlease check and try again.');
            isbnInput.focus();
            return;
        }
        if (await transferToEditPage(isbn)) return;

        const formData = new FormData(form);
        const data = {};
        formData.forEach((v, k) => data[k] = v);

        if (data.shelf_code) {
            try {
                const resp = await fetch(`/shelves/by_code/${encodeURIComponent(data.shelf_code)}`);
                if (resp.ok) {
                    const shelf = await resp.json();
                    data.shelf_id = shelf.shelf_id;
                } else if (data.shelf_code) {
                    const createResp = await fetch('/shelves', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            shelf_code: data.shelf_code,
                            location_description: ''
                        })
                    });
                    if (createResp.ok) {
                        const shelf = await createResp.json();
                        data.shelf_id = shelf.shelf_id;
                    } else {
                        alert('Failed to create shelf.');
                        return;
                    }
                }
            } catch (e) {
                alert('Failed to resolve shelf code.');
                return;
            }
        }
        delete data.shelf_code;

        let url, method;
        const mode = form.getAttribute('data-mode');
        if (mode === 'edit') {
            url = `/books/${isbn}`;
            method = 'PUT';
        } else {
            url = '/books';
            method = 'POST';
        }

        const resp = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (resp.ok) {
            alert('Book saved successfully.');
            window.location.href = '/';
        } else {
            const err = await resp.json();
            alert('Error: ' + (err.description || resp.statusText));
        }
    });

    isbnInput.focus();
});

async function fetchBookInfo() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    const isbn = document.getElementById('isbn').value;
    if (!isbnValidate(isbn)) {
        alert('invalid ISBN');
        isbnInput.focus();
        return;
    }
    if (await transferToEditPage(isbn)) return;
    try {
        if (loadingSpinner) loadingSpinner.style.display = '';
        const response = await fetch(`/books/api/fetch_book_info/${isbn}`);
        if (loadingSpinner) loadingSpinner.style.display = 'none';
        if (!response.ok) {
            console.error('not found online:', e);
            return;
        }
        const book = await response.json();
        const titleInput = document.getElementById('title');
        if (titleInput.value == 'None') titleInput.value = '';
        if (titleInput && !titleInput.value) titleInput.value = book.title || '';

        const authorInput = document.getElementById('author');
        if (authorInput.value == 'None') authorInput.value = '';
        if (authorInput && !authorInput.value) authorInput.value = book.author || '';

        const publisherInput = document.getElementById('publisher');
        if (publisherInput.value == 'None') publisherInput.value = '';
        if (publisherInput && !publisherInput.value) publisherInput.value = book.publisher || '';

        const pubDateInput = document.getElementById('publication_date');
        if (pubDateInput && !pubDateInput.value) pubDateInput.value = book.publication_date || '';

        const coverPathInput = document.getElementById('cover_image_path');
        if (coverPathInput.value == 'None') coverPathInput.value = '';
        if (coverPathInput && !coverPathInput.value)
            coverPathInput.value = book.cover_image_path;

        const coverImg = document.getElementById('cover_preview');
        if (coverImg) {
            coverImg.src = '/' + book.cover_image_path || '';
        }
    } catch (e) {
        console.error('fetch book info failed:', e);
    }
}
