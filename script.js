document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const lengthSlider = document.getElementById('length-slider');
    const lengthValue = document.getElementById('length-value');
    const passwordDisplay = document.getElementById('password-display');
    const messageArea = document.getElementById('message-area');
    const generateBtn = document.getElementById('generate-btn');
    const copyBtn = document.getElementById('copy-btn');
    const copyIcon = document.getElementById('copy-icon');
    const checkIcon = document.getElementById('check-icon');
    const strengthSelector = document.getElementById('strength-selector');

    // Options checkboxes
    const uppercaseCheck = document.getElementById('uppercase');
    const lowercaseCheck = document.getElementById('lowercase');
    const numbersCheck = document.getElementById('numbers');
    const symbolsCheck = document.getElementById('symbols');

    // --- Event Listeners ---

    // Update length display when slider changes
    lengthSlider.addEventListener('input', (event) => {
        lengthValue.textContent = event.target.value;
    });

    // Handle clicks on the strength selector
    strengthSelector.addEventListener('click', (event) => {
        if (event.target.tagName === 'BUTTON') {
            strengthSelector.querySelector('.active').classList.remove('active');
            event.target.classList.add('active');
        }
    });

    // Generate password when button is clicked
    generateBtn.addEventListener('click', generatePassword);

    // Copy password to clipboard
    copyBtn.addEventListener('click', copyToClipboard);

    // --- Core Functions ---

    /**
     * Fetches a new password from the backend API.
     */
    async function generatePassword() {
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generating...';
        passwordDisplay.textContent = '...';
        messageArea.textContent = ''; // Clear previous messages

        const activeStrengthBtn = strengthSelector.querySelector('.strength-btn.active');
        const strength = activeStrengthBtn ? activeStrengthBtn.dataset.strength : 'strong';

        const options = {
            length: parseInt(lengthSlider.value, 10),
            uppercase: uppercaseCheck.checked,
            lowercase: lowercaseCheck.checked,
            numbers: numbersCheck.checked,
            symbols: symbolsCheck.checked,
            strength: strength // Send selected strength level to API
        };

        try {
            const apiUrl = 'http://127.0.0.1:5000/generate';
            
            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(options),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            passwordDisplay.textContent = data.password;
            if (data.warning) {
                messageArea.textContent = data.warning;
            }

        } catch (error) {
            console.error('Error generating password:', error);
            passwordDisplay.textContent = 'Generation Failed';
            messageArea.textContent = `Error: ${error.message}`;
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = 'Generate Password';
        }
    }

    /**
     * Copies the displayed password to the user's clipboard.
     */
    function copyToClipboard() {
        const password = passwordDisplay.textContent;
        if (!password || password.startsWith('Click') || password.startsWith('Generation')) {
            return; // Don't copy placeholder or error text
        }

        if (navigator.clipboard) {
            navigator.clipboard.writeText(password).then(showCopiedFeedback, () => {
                fallbackCopyTextToClipboard(password);
            });
        } else {
            fallbackCopyTextToClipboard(password);
        }
    }
    
    /**
     * A fallback method for copying text for older browsers or insecure contexts.
     */
    function fallbackCopyTextToClipboard(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.opacity = "0";
        document.body.appendChild(textArea);
        textArea.select();
        try {
            if (document.execCommand('copy')) {
                showCopiedFeedback();
            }
        } catch (err) {
            console.error('Fallback copy failed', err);
        }
        document.body.removeChild(textArea);
    }

    /**
     * Provides visual feedback to the user when text is copied.
     */
    function showCopiedFeedback() {
        copyIcon.style.display = 'none';
        checkIcon.style.display = 'inline-block';
        copyBtn.classList.add('copied');

        setTimeout(() => {
            copyIcon.style.display = 'inline-block';
            checkIcon.style.display = 'none';
            copyBtn.classList.remove('copied');
        }, 2000);
    }
});
