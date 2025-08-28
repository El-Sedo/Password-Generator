# app.py
# An enhanced Flask server to generate AI-strengthened passwords with selectable security levels.
# To run:
# 1. Install Flask and Flask-CORS: pip install Flask Flask-CORS
# 2. Run the script: python app.py
# The server will start on http://127.0.0.1:5000

from flask import Flask, request, jsonify
from flask_cors import CORS
import secrets
import string
import re

# Initialize Flask App
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) to allow browser requests
# from the HTML file to the backend server.
CORS(app)

# --- AI Password Strength Logic ---
# This section contains the "AI" logic. It's a rule-based system
# designed to discard weak, predictable, or common passwords based on different criteria.

# A small list of common English words to check against.
COMMON_WORDS = [
    'password', 'admin', 'welcome', '123456', 'qwerty', 'user', 'guest',
    'login', 'test', 'root', 'secret', 'dragon', 'shadow', 'ninja',
    'football', 'monkey', 'master', 'sunshine', 'princess', 'love'
]

# Common keyboard patterns to avoid.
KEYBOARD_PATTERNS = ['qwerty', 'asdfgh', 'zxcvbn', '12345', 'qazwsx']

def check_password_strength(password, level='strong'):
    """
    AI-powered checker to validate password strength based on a requested level.
    It performs universal checks first, then level-specific ones.
    Levels:
    - 'easy': Basic checks, avoids common words and patterns. Good for memorability.
    - 'strong': (Default) Requires a good mix of characters, avoids patterns.
    - 'max': Requires all four character types (upper, lower, digit, symbol).
    """
    # --- Universal Checks (Applied to all levels) ---
    # 1. Check against common words
    if any(word in password.lower() for word in COMMON_WORDS):
        return False
    # 2. Check for repetitive characters (e.g., 'aaa', '111')
    if re.search(r'(.)\1\1', password):
        return False
    # 3. Check against keyboard patterns
    if any(pattern in password.lower() for pattern in KEYBOARD_PATTERNS):
        return False

    # --- Level-Specific Checks ---
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    
    char_type_count = sum([has_upper, has_lower, has_digit, has_symbol])

    if level == 'easy':
        # For 'easy' (readable), passing the universal checks is enough.
        return True
    
    if level == 'strong':
        # 'Strong' passwords must contain at least 3 different character types.
        return char_type_count >= 3

    if level == 'max':
        # 'Maximum' security passwords must contain all 4 character types.
        return char_type_count == 4

    # Default to False if the level is unknown
    return False

# --- API Endpoint for Password Generation ---

@app.route('/generate', methods=['POST'])
def generate_password():
    """
    Generates a password based on user-defined criteria, including a new strength level,
    then validates it with the AI strength checker before returning.
    """
    try:
        data = request.get_json()
        length = int(data.get('length', 16))
        use_upper = data.get('uppercase', True)
        use_lower = data.get('lowercase', True)
        use_numbers = data.get('numbers', True)
        use_symbols = data.get('symbols', True)
        strength_level = data.get('strength', 'strong') # New: Get strength level from request

        # Build the character set based on user preferences
        char_set = ''
        if use_upper: char_set += string.ascii_uppercase
        if use_lower: char_set += string.ascii_lowercase
        if use_numbers: char_set += string.digits
        if use_symbols: char_set += string.punctuation

        if not char_set:
            return jsonify({'error': 'Please select at least one character type.'}), 400

        # --- Generation and AI Validation Loop ---
        # The system will keep generating passwords until one passes the selected strength check.
        # Increased the attempt limit to handle stricter rules.
        for _ in range(100):
            password = ''.join(secrets.choice(char_set) for i in range(length))
            if check_password_strength(password, strength_level):
                return jsonify({'password': password})

        # Fallback: If no password meets the criteria after 100 tries,
        # return the last generated one with a warning. This prevents errors on
        # highly restrictive settings (e.g., short length + max strength).
        password = ''.join(secrets.choice(char_set) for i in range(length))
        return jsonify({
            'password': password,
            'warning': 'Could not meet all strength criteria. Consider more characters or a lower setting.'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- Main Execution ---
if __name__ == '__main__':
    app.run(debug=True)
