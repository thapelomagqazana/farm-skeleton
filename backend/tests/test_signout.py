import pytest
import requests
from app.database import db

# **Base API URLs**
REGISTER_URL = "http://localhost:8000/api/users"
SIGNIN_URL = "http://localhost:8000/auth/signin"
SIGNOUT_URL = "http://localhost:8000/auth/signout"

# **Test Users**
TEST_USERS = [
    {"name": "User One", "email": "user@example.com", "password": "Password123!"},
    {"name": "Admin User", "email": "admin@example.com", "password": "AdminPass@123", "role": "admin"},
]

# **Store authentication tokens**
USER_TOKEN = ""
ADMIN_TOKEN = ""
EXPIRED_TOKEN = "ExpiredJWTToken"
INVALID_TOKEN = "InvalidJWTToken"
REVOKED_TOKEN = "RevokedJWTToken"
LONG_TOKEN = "a" * 1025
WHITESPACE_TOKEN = "   "


@pytest.fixture(scope="module", autouse=True)
def setup_users():
    global USER_TOKEN, ADMIN_TOKEN

    # **Register test users**
    for user in TEST_USERS:
        requests.post(REGISTER_URL, json=user)

    # **Sign in users and store tokens**
    for user in TEST_USERS:
        response = requests.post(SIGNIN_URL, json={"email": user["email"], "password": user["password"]})
        assert response.status_code == 200, f"Failed to sign in {user['email']}"
        if "admin" in user["email"]:
            ADMIN_TOKEN = response.json()["access_token"]
        else:
            USER_TOKEN = response.json()["access_token"]

    yield  # Run tests

    # Cleanup test users directly from MongoDB
    db.users.delete_many({})  # Deletes all test users


# ** POSITIVE TEST CASES**
@pytest.mark.parametrize("auth_token, expected_status", [
    (lambda: USER_TOKEN, 200),  # TC-01: Sign out with a valid user token
    (lambda: ADMIN_TOKEN, 200),  # TC-02: Sign out with an admin token
])
def test_signout_positive(auth_token, expected_status):
    """Tests successful sign-out."""
    headers = {"Authorization": f"Bearer {auth_token()}"}
    response = requests.post(SIGNOUT_URL, headers=headers)
    print(response.json())

    assert response.status_code == expected_status
    assert response.json() == {"message": "Signed out successfully"}


# ** NEGATIVE TEST CASES**
@pytest.mark.parametrize("auth_token, expected_status, expected_error", [
    (None, 401, "Not authenticated"),  # TC-03: No token
    (lambda: EXPIRED_TOKEN, 401, "Invalid token"),  # TC-04: Expired token
    (lambda: INVALID_TOKEN, 401, "Invalid token"),  # TC-05: Invalid token
    (lambda: REVOKED_TOKEN, 401, "Invalid token"),  # TC-06: Revoked token
    (lambda: USER_TOKEN, 401, "Invalid token"),  # TC-07: Sign out twice (replay attack)
])
def test_signout_negative(auth_token, expected_status, expected_error):
    """Tests sign-out with invalid inputs."""
    auth_token = auth_token() if callable(auth_token) else auth_token
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    response = requests.post(SIGNOUT_URL, headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# ** EDGE TEST CASES**
@pytest.mark.parametrize("auth_token, expected_status, expected_error", [
    (lambda: "a", 401, "Invalid token"),  # TC-08: Very short token
    (lambda: LONG_TOKEN, 401, "Invalid token"),  # TC-09: Very long token
    (lambda: WHITESPACE_TOKEN, 401, "Not authenticated"),  # TC-10: Whitespace token
])
def test_signout_edge_cases(auth_token, expected_status, expected_error):
    """Tests edge cases with invalid tokens."""
    auth_token = auth_token() if callable(auth_token) else auth_token
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    response = requests.post(SIGNOUT_URL, headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# ** SECURITY TEST CASES**
@pytest.mark.parametrize("auth_token, expected_status, expected_error", [
    ("' OR 1=1 --", 401, "Invalid token"),  # TC-12: SQL Injection attempt
    ("<script>alert('Hacked!')</script>", 401, "Invalid token"),  # TC-13: XSS attack attempt
])
def test_signout_security(auth_token, expected_status, expected_error):
    """Tests security vulnerabilities in sign-out."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = requests.post(SIGNOUT_URL, headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# def test_brute_force_protection():
#     """Simulates brute force attack and checks rate limiting."""
#     headers = {"Authorization": f"Bearer {USER_TOKEN}"}
#     max_attempts = 10  # Adjust based on rate limit settings

#     for _ in range(max_attempts):
#         requests.post(SIGNOUT_URL, headers=headers)

#     # After multiple requests, should return HTTP 429
#     response = requests.post(SIGNOUT_URL, headers=headers)
#     assert response.status_code == 429


# def test_csrf_protection():
#     """Tests CSRF protection by sending sign-out request from an untrusted origin."""
#     headers = {
#         "Authorization": f"Bearer {USER_TOKEN}",
#         "Referer": "http://malicious-site.com"
#     }
#     response = requests.post(SIGNOUT_URL, headers=headers)

#     assert response.status_code == 403
#     assert "CSRF attack detected" in response.json()["detail"]
