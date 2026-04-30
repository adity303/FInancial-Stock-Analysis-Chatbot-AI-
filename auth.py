import streamlit as st
import uuid
from datetime import datetime, timedelta
from typing import Optional
from database import (
    create_user, get_user_by_username, get_user_by_id,
    hash_password, verify_password, create_session,
    validate_session, delete_session
)

# Session key constants
SESSION_KEY = 'financial_app_session'
USER_ID_KEY = 'user_id'
USERNAME_KEY = 'username'
AUTHENTICATED_KEY = 'authenticated'

def init_auth():
    """Initialize authentication in session state."""
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = None
    if AUTHENTICATED_KEY not in st.session_state:
        st.session_state[AUTHENTICATED_KEY] = False
    if USER_ID_KEY not in st.session_state:
        st.session_state[USER_ID_KEY] = None
    if USERNAME_KEY not in st.session_state:
        st.session_state[USERNAME_KEY] = None

def signup(username: str, email: str, password: str) -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success, message).
    """
    if not username or not email or not password:
        return False, "All fields are required."

    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Please enter a valid email address."

    password_hash = hash_password(password)
    user_id = create_user(username, email, password_hash)

    if user_id is None:
        return False, "Username or email already exists."

    # Auto-login after signup
    session_id = str(uuid.uuid4())
    expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
    create_session(session_id, user_id, expires_at)

    st.session_state[SESSION_KEY] = session_id
    st.session_state[AUTHENTICATED_KEY] = True
    st.session_state[USER_ID_KEY] = user_id
    st.session_state[USERNAME_KEY] = username

    return True, "Account created successfully!"

def login(username: str, password: str) -> tuple[bool, str]:
    """
    Authenticate a user.
    Returns (success, message).
    """
    if not username or not password:
        return False, "Username and password are required."

    user = get_user_by_username(username)

    if user is None:
        return False, "Invalid username or password."

    if not verify_password(user['password_hash'], password):
        return False, "Invalid username or password."

    # Create session
    session_id = str(uuid.uuid4())
    expires_at = (datetime.utcnow() + timedelta(days=7)).isoformat()
    create_session(session_id, user['id'], expires_at)

    st.session_state[SESSION_KEY] = session_id
    st.session_state[AUTHENTICATED_KEY] = True
    st.session_state[USER_ID_KEY] = user['id']
    st.session_state[USERNAME_KEY] = user['username']

    return True, "Login successful!"

def logout():
    """Log out the current user."""
    if st.session_state.get(SESSION_KEY):
        delete_session(st.session_state[SESSION_KEY])

    st.session_state[SESSION_KEY] = None
    st.session_state[AUTHENTICATED_KEY] = False
    st.session_state[USER_ID_KEY] = None
    st.session_state[USERNAME_KEY] = None

    # Clear all other session state
    for key in list(st.session_state.keys()):
        if key not in [SESSION_KEY, AUTHENTICATED_KEY, USER_ID_KEY, USERNAME_KEY]:
            del st.session_state[key]

def is_authenticated() -> bool:
    """Check if user is authenticated."""
    init_auth()

    # If already marked as authenticated, verify session is still valid
    if st.session_state[AUTHENTICATED_KEY] and st.session_state[SESSION_KEY]:
        user_id = validate_session(st.session_state[SESSION_KEY])
        if user_id:
            st.session_state[USER_ID_KEY] = user_id
            return True
        else:
            # Session expired or invalid
            logout()
            return False

    return st.session_state[AUTHENTICATED_KEY]

def get_current_user_id() -> Optional[int]:
    """Get the current user's ID."""
    return st.session_state.get(USER_ID_KEY)

def get_current_username() -> Optional[str]:
    """Get the current user's username."""
    return st.session_state.get(USERNAME_KEY)

def require_auth():
    """Require authentication; redirect to login if not authenticated."""
    if not is_authenticated():
        st.warning("Please log in to access this feature.")
        return False
    return True
