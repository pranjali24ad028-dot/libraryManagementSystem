const result = document.getElementById('book-list');
const issueResult = document.getElementById('issue-result');
const returnResult = document.getElementById('return-result');
const reportOutput = document.getElementById('report-output');

async function apiFetch(path, options = {}) {
    const res = await fetch(path, options);
    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || 'Request failed');
    }
    return res.json();
}

async function loadBooks() {
    try {
        const books = await apiFetch('/api/books');
        if (books.length === 0) {
            result.innerHTML = '<p>No books available.</p>';
            return;
        }
        result.innerHTML = `
            <table>
                <thead><tr><th>ID</th><th>Title</th><th>Category</th><th>Price</th><th>Available</th></tr></thead>
                <tbody>
                    ${books.map(book => `
                        <tr>
                            <td>${book.book_id}</td>
                            <td>${book.title}</td>
                            <td>${book.category}</td>
                            <td>${book.price.toFixed(2)}</td>
                            <td>${book.availability}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        result.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

async function loadReport(reportName) {
    let endpoint = '/api/reports/categories';
    switch (reportName) {
        case 'over-average':
            endpoint = '/api/reports/over-average';
            break;
        case 'never-issued':
            endpoint = '/api/books/never-issued';
            break;
    }
    try {
        const data = await apiFetch(endpoint);
        if (!data.length) {
            reportOutput.innerHTML = '<p>No results.</p>';
            return;
        }
        reportOutput.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (error) {
        reportOutput.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

const issueForm = document.getElementById('issue-form');
issueForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(issueForm);
    const body = {
        member_id: parseInt(formData.get('member_id'), 10),
        book_id: parseInt(formData.get('book_id'), 10),
        issue_date: formData.get('issue_date') || undefined
    };
    try {
        const response = await apiFetch('/api/issue', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        issueResult.textContent = `Issued successfully. Issue ID: ${response.issue_id}`;
        loadBooks();
    } catch (error) {
        issueResult.textContent = error.message;
    }
});

const returnForm = document.getElementById('return-form');
returnForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(returnForm);
    const body = {
        issue_id: parseInt(formData.get('issue_id'), 10),
        return_date: formData.get('return_date') || undefined
    };
    try {
        const response = await apiFetch('/api/return', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        returnResult.textContent = `Book returned successfully.`;
        loadBooks();
    } catch (error) {
        returnResult.textContent = error.message;
    }
});

window.onload = () => {
    loadBooks();
};
