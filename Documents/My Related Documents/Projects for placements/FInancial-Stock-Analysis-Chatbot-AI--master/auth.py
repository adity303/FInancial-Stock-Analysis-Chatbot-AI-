import csv
import hashlib
import os

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# CSV file for storing users
USERS_FILE = "users.csv"

# Create CSV file if it doesn't exist
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'password'])

# Validate username (max 12 characters)
def validate_username(username):
    if len(username) > 12:
        return False, "Username must be 12 characters or less"
    if len(username) == 0:
        return False, "Username cannot be empty"
    return True, "Valid"

# Validate password (4-6 characters)
def validate_password(password):
    if len(password) < 4 or len(password) > 6:
        return False, "Password must be 4-6 characters long"
    if len(password) == 0:
        return False, "Password cannot be empty"
    return True, "Valid"

# Read all users from CSV
def read_users():
    users = {}
    with open(USERS_FILE, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            users[row['username']] = row['password']
    return users

# Register User 
def register_user(username, password):
    # Validate inputs
    is_valid_username, username_msg = validate_username(username)
    if not is_valid_username:
        return False, username_msg
    
    is_valid_password, password_msg = validate_password(password)
    if not is_valid_password:
        return False, password_msg
    
    # Check if username already exists
    users = read_users()
    if username in users:
        return False, "Username already exists"
    
    # Add user to CSV
    with open(USERS_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, hash_password(password)])
    
    return True, "Account created successfully"

# Login user 
def login_user(username, password):
    users = read_users()
    hashed_password = hash_password(password)
    
    if username in users and users[username] == hashed_password:
        return True, username
    return False, "Invalid credentials"