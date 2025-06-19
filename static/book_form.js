document.addEventListener('DOMContentLoaded', function () {
    const isbnInput = document.getElementById('isbn');
    const form = document.getElementById('manageBookForm');

    if (!isbnInput) {
        console.error('ISBN input not found');
        return;
    }

    isbnInput.addEventListener('change', async function () {
        const isbn = isbnInput.value;
        if (!isbn) return;
        const resp = await fetch(`/books/${isbn}`);
        if (resp.status === 404) {
            await fetchBookInfo();
        } else if (resp.ok) {
            window.location.href = `/books/manage?isbn=${isbn}`;
        }
    });

    if (form && form.querySelector('input[name="isbn"]:not([readonly])')) {
        form.addEventListener('submit', async function (e) {
            const isbn = isbnInput.value;
            if (!isbn) return;
            const resp = await fetch(`/books/${isbn}`);
            if (resp.status === 404) {
                await fetchBookInfo();
            }

        });
    }

    isbnInput.focus();
});

async function fetchBookInfo() {
    const isbn = document.getElementById('isbn').value;
    if (!isbn) {
        alert('ISBNを入力してください');
        return;
    }
    try {
        const response = await fetch(`/books/api/fetch_book_info/${isbn}`);
        if (!response.ok) {
            alert('書籍情報が見つかりませんでした');
            return;
        }
        const book = await response.json();
        const titleInput = document.getElementById('title');
        if (titleInput && !titleInput.value) titleInput.value = book.title || '';

        const authorInput = document.getElementById('author');
        if (authorInput && !authorInput.value) authorInput.value = book.author || '';

        const publisherInput = document.getElementById('publisher');
        if (publisherInput && !publisherInput.value) publisherInput.value = book.publisher || '';

        const pubDateInput = document.getElementById('publication_date');
        if (pubDateInput && !pubDateInput.value) pubDateInput.value = book.publication_date || '';

        const coverPathInput = document.getElementById('cover_image_path');
        if (coverPathInput && !coverPathInput.value)
            coverPathInput.value = book.cover_image_path;

        const coverImg = document.getElementById('cover_preview');
        if (coverImg) {
            coverImg.src = '/' + book.cover_image_path || '';
        }


    } catch (e) {
        console.error('書籍情報の取得に失敗:', e);
    }
}
