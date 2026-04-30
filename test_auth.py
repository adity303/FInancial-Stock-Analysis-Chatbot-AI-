#!/usr/bin/env python3
"""Quick test of authentication and database functionality."""

import sys
sys.path.insert(0, '.')

from database import init_db, create_user, get_user_by_username, hash_password, verify_password, add_to_watchlist, get_watchlist, save_portfolio, get_user_portfolios
from auth import signup, login, logout, is_authenticated, get_current_user_id, get_current_username

def test_auth_flow():
    print("Testing Authentication System...")

    # Initialize database
    init_db()
    print("Database initialized")

    # Test signup
    print("\nTesting signup...")
    success, message = signup("testuser", "test@example.com", "testpass123")
    if success:
        print(f"Signup successful: {message}")
    else:
        print(f"Signup failed: {message}")
        return False

    # Check authentication state
    if is_authenticated():
        print(f"User authenticated: {get_current_username()}")
    else:
        print("User not authenticated")
        return False

    # Test watchlist
    user_id = get_current_user_id()
    print(f"\nTesting watchlist for user ID: {user_id}")

    add_to_watchlist(user_id, "AAPL")
    add_to_watchlist(user_id, "GOOGL")
    add_to_watchlist(user_id, "MSFT")
    print("Added 3 stocks to watchlist")

    watchlist = get_watchlist(user_id)
    print(f"Watchlist contains: {watchlist}")

    # Test portfolio saving
    print("\nTesting portfolio saving...")
    import json
    test_portfolio = {
        "Safe Portfolio": {
            "percentages": {"Equity": 25, "Debt": 50, "Gold": 15, "Cash": 10},
            "amounts": {"Equity": 12500, "Debt": 25000, "Gold": 7500, "Cash": 5000},
            "expected_annual_return": 8.5,
            "risk_level": "Low"
        }
    }
    portfolio_json = json.dumps(test_portfolio)
    pf_id = save_portfolio(user_id, "Test Portfolio", 25, "Low", 50000, portfolio_json)
    print(f"Portfolio saved with ID: {pf_id}")

    portfolios = get_user_portfolios(user_id)
    print(f"User has {len(portfolios)} portfolio(s)")

    # Test logout
    print("\nTesting logout...")
    logout()
    if not is_authenticated():
        print("Logout successful")
    else:
        print("Logout failed")
        return False

    # Test login
    print("\nTesting login...")
    success, message = login("testuser", "testpass123")
    if success:
        print(f"Login successful: {message}")
    else:
        print(f"Login failed: {message}")
        return False

    print("\nAll tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_auth_flow()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
