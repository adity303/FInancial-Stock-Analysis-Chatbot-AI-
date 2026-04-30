import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

# Database file path
DB_PATH = "financial_app.db"

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Watchlists table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, ticker)
        )
    """)

    # Portfolios table (stores saved portfolio recommendations)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            risk_tolerance TEXT,
            budget REAL,
            portfolio_data TEXT NOT NULL,  -- JSON string of portfolio allocation
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # User sessions table (for tracking active sessions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

def create_user(username: str, email: str, password_hash: str) -> Optional[int]:
    """Create a new user and return user ID if successful."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve user by username."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve user by ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def verify_password(stored_hash: str, provided_password: str) -> bool:
    """Verify a password against its hash."""
    import bcrypt
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Watchlist functions
def add_to_watchlist(user_id: int, ticker: str) -> bool:
    """Add a stock ticker to user's watchlist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO watchlists (user_id, ticker) VALUES (?, ?)",
            (user_id, ticker.upper())
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # Already exists

def remove_from_watchlist(user_id: int, ticker: str) -> bool:
    """Remove a stock ticker from user's watchlist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM watchlists WHERE user_id = ? AND ticker = ?",
        (user_id, ticker.upper())
    )
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def get_watchlist(user_id: int) -> List[str]:
    """Get all tickers in user's watchlist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT ticker FROM watchlists WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def is_in_watchlist(user_id: int, ticker: str) -> bool:
    """Check if a ticker is in user's watchlist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM watchlists WHERE user_id = ? AND ticker = ?",
        (user_id, ticker.upper())
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Portfolio functions
def save_portfolio(user_id: int, name: str, age: int, risk_tolerance: str, budget: float, portfolio_data: str) -> int:
    """Save a portfolio recommendation for a user. Returns portfolio ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO portfolios (user_id, name, age, risk_tolerance, budget, portfolio_data)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, name, age, risk_tolerance, budget, portfolio_data)
    )
    portfolio_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return portfolio_id

def get_user_portfolios(user_id: int) -> List[Dict[str, Any]]:
    """Get all portfolios for a user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, name, age, risk_tolerance, budget, portfolio_data, created_at
           FROM portfolios WHERE user_id = ? ORDER BY created_at DESC""",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_portfolio(portfolio_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific portfolio by ID (ensuring it belongs to the user)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM portfolios WHERE id = ? AND user_id = ?",
        (portfolio_id, user_id)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_portfolio(portfolio_id: int, user_id: int) -> bool:
    """Delete a portfolio belonging to a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM portfolios WHERE id = ? AND user_id = ?",
        (portfolio_id, user_id)
    )
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

# Session management functions
def create_session(session_id: str, user_id: int, expires_at: str) -> bool:
    """Create a new session for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO sessions (session_id, user_id, expires_at) VALUES (?, ?, ?)",
        (session_id, user_id, expires_at)
    )
    conn.commit()
    conn.close()
    return True

def validate_session(session_id: str) -> Optional[int]:
    """Validate a session and return user_id if valid, None otherwise."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT user_id FROM sessions
           WHERE session_id = ? AND expires_at > datetime('now')""",
        (session_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def delete_session(session_id: str) -> bool:
    """Delete a session (logout)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return True

# Initialize database on module import
if not os.path.exists(DB_PATH):
    init_db()
