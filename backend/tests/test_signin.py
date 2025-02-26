import pytest
import requests
import time
from app.database import db

# Base API URLs
BASE_URL = "http://localhost:8000/auth/signin"
USER_REGISTRATION_URL = "http://localhost:8000/api/users"

# Test Users
TEST_USERS = [
    {"email": "validuser@example.com", "password": "StrongPass123%"},
    {"email": "VALIDUSER@example.com", "password": "StrongPass123%"},
    {"email": "valid.user+test@example.com", "password": "StrongPass123%"},
    {"email": "user@sub.example.co.uk", "password": "SecurePass1!"},
    {"email": "newuser@example.com", "password": "NewPass123!"},
]

# Setup: Register test users
@pytest.fixture(scope="module", autouse=True)
def setup_users():
    """Ensures test users exist before running tests."""
    for user in TEST_USERS:
        requests.post(USER_REGISTRATION_URL, json={"name": "Test User", **user})

    yield  # Run tests
    # Cleanup test users directly from MongoDB
    db.users.delete_many({})  # Deletes all test users


# POSITIVE TEST CASES
@pytest.mark.parametrize("payload, expected_status", [
    ({"email": "validuser@example.com", "password": "StrongPass123%"}, 200),
    ({"email": "VALIDUSER@example.com", "password": "StrongPass123%"}, 200),
    ({"email": "valid.user+test@example.com", "password": "StrongPass123%"}, 200),
    ({"email": "user@sub.example.co.uk", "password": "SecurePass1!"}, 200),
    ({"email": "newuser@example.com", "password": "NewPass123!"}, 200),
])
def test_signin_positive(payload, expected_status):
    """Tests valid user sign-ins."""
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == expected_status
    assert "access_token" in response.json()


# NEGATIVE TEST CASES
@pytest.mark.parametrize("payload, expected_status, expected_error", [
    ({"password": "Pass1234"}, 422, 'Field required'),
    ({"email": "user@example.com"}, 422, 'Field required'),
    ({"email": "invalid-email", "password": "Pass1234"}, 422, 'value is not a valid email address: An email address must have an @-sign.'),
    ({"email": "user@example.com", "password": ""}, 422, "password cannot be empty"),
])
def test_signin_negative(payload, expected_status, expected_error):
    """Tests invalid user sign-ins."""
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == expected_status
    error_messages = [error["msg"] for error in response.json()["detail"]]

    # Ensure expected error message is in the response
    assert expected_error in error_messages

# NEGATIVE TEST CASES INVALID PASSWORD OR EMAIL
@pytest.mark.parametrize("payload, expected_status, expected_error", [
    ({"email": "validuser@example.com", "password": "WrongPass123%"}, 401, "Invalid email or password"),
    ({"email": "unknown@example.com", "password": "Pass1234%!"}, 401, "Invalid email or password"),
])
def test_signin_negative(payload, expected_status, expected_error):
    """Tests invalid user sign-ins."""
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == expected_status

    # Ensure expected error message is the response
    assert expected_error == response.json()["detail"]

# EDGE TEST CASES
@pytest.mark.parametrize("payload, expected_status", [
    ({"email": "   validuser@example.com", "password": "StrongPass123%"}, 200),
    ({"email": "validuser@example.com   ", "password": "StrongPass123%"}, 200),
    ({"email": "ValidUser@Example.com", "password": "StrongPass123%"}, 200),
    ({"email": "", "password": "StrongPass123%"}, 422),
    ({}, 422),
])
def test_signin_edge_cases(payload, expected_status):
    """Tests sign-in at boundary conditions."""
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == expected_status


# SECURITY TEST CASES
@pytest.mark.parametrize("payload, expected_status", [
    ({"email": "admin' OR '1'='1", "password": "Pass1234%"}, 422),
    ({"email": "<script>alert('Hacked!')</script>", "password": "Pass1234%"}, 422),
])
def test_signin_security(payload, expected_status):
    """Tests sign-in against SQL Injection & XSS attacks."""
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == expected_status


# def test_brute_force_attack():
#     """Simulates brute force attack and checks if API enforces rate limiting."""
#     email = "validuser@example.com"
#     password = "WrongPass123%"
#     max_attempts = 10  # Adjust based on rate limit settings

#     for _ in range(max_attempts):
#         requests.post(BASE_URL, json={"email": email, "password": password})

#     # After multiple failures, should return HTTP 429
#     response = requests.post(BASE_URL, json={"email": email, "password": password})
#     assert response.status_code == 429


def test_csrf_attack():
    """Simulates CSRF attack by sending request without proper headers."""
    headers = {"Referer": "http://malicious-site.com"}  # Fake Referer
    response = requests.post(BASE_URL, json={"email": "validuser@example.com", "password": "StrongPass123%"}, headers=headers)
    assert response.status_code == 403  # Expect Forbidden


# def test_replay_attack():
#     """Tests if old tokens cannot be reused."""
#     # Step 1: Sign in and get token
#     response = requests.post(BASE_URL, json={"email": "validuser@example.com", "password": "StrongPass123%"})
#     assert response.status_code == 200
#     token = response.json()["access_token"]

#     # Step 2: Wait for token expiry (assuming short expiry for test)
#     time.sleep(2)  # Adjust based on token expiry settings

#     # Step 3: Try using expired token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = requests.get("http://localhost:8000/protected-route", headers=headers)  # Example protected route
#     assert response.status_code == 401  # Expect Unauthorized
