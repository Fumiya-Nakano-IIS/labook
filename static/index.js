document.addEventListener('DOMContentLoaded', async function () {
    const tableBody = document.querySelector('#booksTable tbody');
    try {
        const resp = await fetch('/books?sort=updatedtime&order=desc&limit=20');
        const books = await resp.json();
        tableBody.innerHTML = '';
        for (const book of books) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><img src="${book.cover_image_path || ''}" alt="Cover Image" style="max-width: 100px; max-height: 100px;" /></td>
                <td>${book.isbn}</td>
                <td>${book.title}</td>
                <td>${book.author || ''}</td>
                <td>${book.publisher || ''}</td>
                <td>${book.publication_date || ''}</td>
                <td>${book.status || ''}</td>
            `;
            tableBody.appendChild(tr);
        }
    } catch (e) {
        tableBody.innerHTML = '<tr><td colspan="7">Failed to load books</td></tr>';
    }
});