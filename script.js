// static/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Core elements
    const preprocessBtn = document.getElementById('preprocessBtn');
    const uploadBtn = document.getElementById('uploadBtn');
    const inputText = document.getElementById('inputText');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const results = document.getElementById('results');
    const batchResults = document.getElementById('batchResults');

    // File upload elements
    const fileUpload = document.getElementById('fileUpload');
    const fileDropZone = document.getElementById('fileDropZone');
    const csvColumnDiv = document.getElementById('csvColumnDiv');

    // --- NEW: Drag and Drop Functionality ---
    fileDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileDropZone.classList.add('dragover');
    });
    fileDropZone.addEventListener('dragleave', () => {
        fileDropZone.classList.remove('dragover');
    });
    fileDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        fileDropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length) {
            fileUpload.files = files;
            // Manually trigger change event
            fileUpload.dispatchEvent(new Event('change'));
        }
    });
    fileDropZone.addEventListener('click', () => {
        fileUpload.click();
    });
    
    // Show/hide CSV column input based on file type
    fileUpload.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            const fileName = this.files[0].name;
            uploadBtn.disabled = false;
            fileDropZone.querySelector('p').textContent = `File selected: ${fileName}`;
            if (fileName.endsWith('.csv')) {
                csvColumnDiv.style.display = 'block';
            } else {
                csvColumnDiv.style.display = 'none';
            }
        } else {
            uploadBtn.disabled = true;
            fileDropZone.querySelector('p').textContent = `Drag & drop your .txt or .csv file here`;
            csvColumnDiv.style.display = 'none';
        }
    });

    // Preprocess single text
    preprocessBtn.addEventListener('click', function() {
        const text = inputText.value.trim();
        if (!text) {
            showToast('Please enter some text to preprocess.', 'warning');
            return;
        }
        const options = getPreprocessingOptions();
        
        showLoading(true);
        hideResults();

        fetch('/preprocess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, ...options })
        })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                displayResults(data.result);
                showToast('Text processed successfully!', 'success');
            } else {
                showToast(data.error || 'An error occurred.', 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            showToast('Network error: ' + error.message, 'danger');
        });
    });

    // Process uploaded file
    uploadBtn.addEventListener('click', function() {
        if (!fileUpload.files.length) {
            showToast('Please select a file to upload.', 'warning');
            return;
        }
        const file = fileUpload.files[0];
        const formData = new FormData();
        formData.append('file', file);
        
        const options = getPreprocessingOptions();
        for (const [key, value] of Object.entries(options)) {
            formData.append(key, value.toString());
        }

        if (file.name.endsWith('.csv')) {
            const textColumn = document.getElementById('textColumn').value.trim();
            formData.append('textColumn', textColumn || 'text');
        }

        showLoading(true);
        hideResults();

        fetch('/upload', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            if (data.success) {
                displayBatchResults(data.results);
                showToast(`Successfully processed ${data.count} items!`, 'success');
            } else {
                showToast(data.error || 'An error occurred.', 'danger');
            }
        })
        .catch(error => {
            showLoading(false);
            showToast('Network error: ' + error.message, 'danger');
        });
    });

    function getPreprocessingOptions() {
        return {
            lowercase: document.getElementById('lowercase').checked,
            removePunctuation: document.getElementById('removePunctuation').checked,
            removeSpecial: document.getElementById('removeSpecial').checked,
            tokenize: document.getElementById('tokenize').checked,
            removeStopwords: document.getElementById('removeStopwords').checked,
            lemmatize: document.getElementById('lemmatize').checked,
            stem: document.getElementById('stem').checked
        };
    }

    function showLoading(show) {
        loadingSpinner.style.display = show ? 'block' : 'none';
        preprocessBtn.disabled = show;
        uploadBtn.disabled = show;
    }

    function hideResults() {
        results.style.display = 'none';
        batchResults.style.display = 'none';
    }

    function displayResults(result) {
        document.getElementById('originalText').textContent = result.original_text;
        document.getElementById('processedText').textContent = result.processed_text;
        document.getElementById('tokenCount').textContent = result.token_count;
        
        const tokensContainer = document.getElementById('tokens');
        tokensContainer.innerHTML = '';
        
        result.tokens.forEach((token, index) => {
            const tokenSpan = document.createElement('span');
            tokenSpan.className = 'token';
            tokenSpan.textContent = token;
            tokenSpan.style.animationDelay = `${index * 0.02}s`;
            tokensContainer.appendChild(tokenSpan);
        });
        results.style.display = 'block';
    }

    function displayBatchResults(batchData) {
        const tbody = document.getElementById('batchResultsBody');
        tbody.innerHTML = '';
        batchData.forEach(result => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><div class="text-truncate" style="max-width: 200px;">${result.original_text}</div></td>
                <td><div class="text-truncate" style="max-width: 200px;">${result.processed_text}</div></td>
                <td><div class="text-truncate" style="max-width: 200px;">${result.tokens ? result.tokens.join(', ') : 'N/A'}</div></td>
                <td><span class="badge rounded-pill bg-primary">${result.token_count}</span></td>
            `;
            tbody.appendChild(row);
        });
        batchResults.style.display = 'block';
    }

    // --- NEW: Toast Notification Functionality ---
    function showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container');
        const toastId = 'toast-' + Date.now();
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastElement = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastElement, { delay: 5000 });
        toast.show();
        toastElement.addEventListener('hidden.bs.toast', () => toastElement.remove());
    }

    // --- NEW: Copy to Clipboard Functionality ---
    document.body.addEventListener('click', (e) => {
        const copyBtn = e.target.closest('.copy-btn');
        if (!copyBtn) return;

        let textToCopy = '';
        if (copyBtn.hasAttribute('data-clipboard-target')) {
            const targetElement = document.querySelector(copyBtn.dataset.clipboardTarget);
            textToCopy = targetElement.textContent;
        } else if (copyBtn.hasAttribute('data-clipboard-tokens')) {
            const tokens = Array.from(document.querySelectorAll('#tokens .token')).map(t => t.textContent);
            textToCopy = tokens.join(' ');
        }
        
        if (textToCopy) {
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalContent = copyBtn.innerHTML;
                copyBtn.innerHTML = `<i class="fas fa-check"></i> Copied!`;
                copyBtn.disabled = true;
                setTimeout(() => {
                    copyBtn.innerHTML = originalContent;
                    copyBtn.disabled = false;
                }, 2000);
            }).catch(err => {
                showToast('Failed to copy text.', 'danger');
                console.error('Clipboard error:', err);
            });
        }
    });
});