import json
import os
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

USERS_FILE = 'data/users.json'

def load_users():
    """Load users from JSON file."""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump([], f)
        return []
    
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_users(users):
    """Save users to JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_user_by_username(username):
    """Get user by username."""
    users = load_users()
    for user in users:
        if user.get('username') == username:
            return user
    return None

def register_user(username, password):
    """Register a new user."""
    users = load_users()
    
    # Check if username already exists
    if any(user.get('username') == username for user in users):
        raise ValueError(f"Username '{username}' already exists")
    
    # Create new user
    new_user = {
        'id': str(uuid.uuid4()),
        'username': username,
        'password': generate_password_hash(password),
        'created_at': datetime.now().isoformat()
    }
    
    users.append(new_user)
    save_users(users)
    return new_user

def authenticate_user(username, password):
    """Authenticate user."""
    user = get_user_by_username(username)
    if user and check_password_hash(user.get('password'), password):
        return True
    return False
