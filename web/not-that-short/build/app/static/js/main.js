document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('urlInput');
    const shortenButton = document.getElementById('shortenButton');
    const resultContainer = document.querySelector('.result-container');
    const shortUrlInput = document.getElementById('shortUrl');
    const copyButton = document.getElementById('copyButton');

    shortenButton.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        const shortcode = document.getElementById('shortcodeInput').value.trim();
        if (shortcode && (shortcode.length < 5 || shortcode.length > 50)) {
            showError('Custom shortcode must be between 5 and 50 characters');
            return;
        }

        if (shortcode && !/^[a-zA-Z0-9]+$/.test(shortcode)) {
            showError('Custom shortcode can only contain letters and numbers');
            return;
        }

        if (!url) {
            showError('Please enter a URL');
            return;
        }

        if (!isValidUrl(url)) {
            showError('Please enter a valid URL');
            return;
        }

        try {
            const response = await fetch('/shorten', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    url: url,
                    short_code: shortcode || null
                })
            });

            if (!response.ok) {
                throw new Error(response.statusText);
            }

            const data = await response.json();
            showResult(data.short_url);
        } catch (error) {
            showError('Failed to shorten URL: ' + error.message);
        }
    });

    copyButton.addEventListener('click', () => {
        shortUrlInput.select();
        document.execCommand('copy');
        showSuccess('Copied to clipboard!');
    });

    function showResult(shortUrl) {
        shortUrlInput.value = shortUrl;
        resultContainer.classList.remove('hidden');
        removeMessages();
    }

    function showError(message) {
        removeMessages();
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        resultContainer.parentNode.insertBefore(errorDiv, resultContainer);
    }

    function showSuccess(message) {
        removeMessages();
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        resultContainer.parentNode.insertBefore(successDiv, resultContainer.nextSibling);
    }

    function removeMessages() {
        document.querySelectorAll('.error-message, .success-message').forEach(el => el.remove());
    }

    function isValidUrl(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (_) {
            return false;
        }
    }
});
