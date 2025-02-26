import pytest
import requests
from app.database import db

# Base API URLs
BASE_URL = "http://localhost:8000/api/users"
SIGNIN_URL = "http://localhost:8000/auth/signin"
REGISTER_URL = "http://localhost:8000/api/users"

# Test Users
TEST_USERS = [
    {"name": "John Doe", "email": "john@example.com", "password": "Password123!", "role": "admin"},
    {"name": "Jane Doe", "email": "jane@example.com", "password": "Password123!", "role": "user"},
]

# Store authentication token and user IDs
TOKEN = ""
ADMIN_TOKEN = ""
USER_IDS = {}

# Reset Rate Limit Before Each Test Case
@pytest.fixture(autouse=True)
def reset_rate_limit():
    global TOKEN, ADMIN_TOKEN, USER_IDS

    # Create test users
    for user in TEST_USERS:
        response = requests.post(REGISTER_URL, json=user)
        if response.status_code == 201:
            user_id = response.json()["id"]
            USER_IDS[user["email"]] = user_id

    # Authenticate and get a JWT token for normal user
    response = requests.post(SIGNIN_URL, json={"email": TEST_USERS[1]["email"], "password": TEST_USERS[1]["password"]})
    assert response.status_code == 200
    TOKEN = response.json()["access_token"]

    # Authenticate and get a JWT token for admin
    response = requests.post(SIGNIN_URL, json={"email": TEST_USERS[0]["email"], "password": TEST_USERS[0]["password"]})
    assert response.status_code == 200
    ADMIN_TOKEN = response.json()["access_token"]

    yield  # Run tests

    # Cleanup test users directly from MongoDB
    db.users.delete_many({})  # Deletes all test users




# **Positive Test Cases**
@pytest.mark.parametrize("user_id, auth_token, expected_status", [
    (lambda: USER_IDS["jane@example.com"], lambda: ADMIN_TOKEN, 200),  # TC-01: Delete a regular user (by admin)
    (lambda: USER_IDS["john@example.com"], lambda: ADMIN_TOKEN, 200),  # TC-02: Admin deletes self
])
def test_delete_user_positive(user_id, auth_token, expected_status):
    """Tests deleting users with valid inputs."""
    headers = {"Authorization": f"Bearer {auth_token()}"}
    response = requests.delete(f"{BASE_URL}/{user_id()}", headers=headers)

    assert response.status_code == expected_status
    assert response.json()["message"] == "User deleted successfully"


# **Negative Test Cases**
@pytest.mark.parametrize("user_id, auth_token, expected_status, expected_error", [
    # ("non_existent_id", lambda: ADMIN_TOKEN, 404, "User not found"),  # TC-03: Non-existent user
    ("invalid123", lambda: ADMIN_TOKEN, 400, "Invalid user ID format"),  # TC-04: Invalid ID format
    (lambda: USER_IDS["john@example.com"], lambda: TOKEN, 403, "Forbidden: Access denied"),  # TC-05: User deletes another user
    (lambda: USER_IDS["jane@example.com"], None, 401, "Not authenticated"),  # TC-06: No token
    (lambda: USER_IDS["jane@example.com"], "ExpiredJWTToken", 401, 'Invalid token'),  # TC-07: Expired token
    (lambda: USER_IDS["jane@example.com"], "InvalidJWTToken", 401, "Invalid token"),  # TC-08: Invalid token
])
def test_delete_user_negative(user_id, auth_token, expected_status, expected_error):
    """Tests deleting users with invalid inputs."""
    # Ensure user_id is correctly retrieved whether it's a lambda function or a string
    user_id = user_id() if callable(user_id) else user_id
    auth_token = auth_token() if callable(auth_token) else auth_token
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    response = requests.delete(f"{BASE_URL}/{user_id}", headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# **Edge Test Cases**
@pytest.mark.parametrize("user_id, auth_token, expected_status, expected_error", [
    ("1", lambda: ADMIN_TOKEN, 400, "Invalid user ID format"),  # TC-09: Short ID
    ("x" * 256, lambda: ADMIN_TOKEN, 400, "Invalid user ID format"),  # TC-10: Long ID
])
def test_delete_user_edge_cases(user_id, auth_token, expected_status, expected_error):
    """Tests deleting users at boundary conditions."""
    # Ensure user_id is correctly retrieved whether it's a lambda function or a string
    user_id = user_id() if callable(user_id) else user_id
    auth_token = auth_token() if callable(auth_token) else auth_token
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    response = requests.delete(f"{BASE_URL}/{user_id}", headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# **Security Test Cases**
@pytest.mark.parametrize("user_id, auth_token, expected_status, expected_error", [
    ("' OR 1=1 --", lambda: ADMIN_TOKEN, 400, "Invalid user ID format"),  # TC-11: SQL Injection
    # ("<script>alert('Hacked!')</script>", lambda: ADMIN_TOKEN, 404, "Invalid user ID format"),  # TC-12: XSS Attack
])
def test_delete_user_security(user_id, auth_token, expected_status, expected_error):
    """Tests deleting users with security vulnerabilities."""
    # Ensure user_id is correctly retrieved whether it's a lambda function or a string
    user_id = user_id() if callable(user_id) else user_id
    auth_token = auth_token() if callable(auth_token) else auth_token
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    response = requests.delete(f"{BASE_URL}/{user_id}", headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# # **Brute Force Protection Test**
# def test_brute_force_protection():
#     """Simulates brute force attack and checks rate limiting."""
#     headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
#     user_id = list(USER_IDS.values())[0]  # Get any valid user ID
#     max_attempts = 10  # Adjust based on rate limit settings

#     for _ in range(max_attempts):
#         requests.delete(f"{BASE_URL}/{user_id}", headers=headers)

#     # After multiple requests, should return HTTP 429
#     response = requests.delete(f"{BASE_URL}/{user_id}", headers=headers)
#     print(response.json())
#     assert response.status_code == 429


# # **Revoked Token Test**
# @pytest.mark.parametrize("user_id, auth_token, expected_status, expected_error", [
#     (lambda: USER_IDS["jane@example.com"], "RevokedJWTToken", 401, "Invalid token"),  # TC-14: Revoked token
#     (lambda: USER_IDS["john@example.com"], lambda: TOKEN, 403, "Forbidden: Access denied"),  # TC-15: Unauthorized deletion
# ])
# def test_delete_user_revoked_token(user_id, auth_token, expected_status, expected_error):
#     """Tests deleting users with revoked or unauthorized tokens."""
#     headers = {"Authorization": f"Bearer {auth_token()}"} if auth_token else {}
#     response = requests.delete(f"{BASE_URL}/{user_id()}", headers=headers)

#     assert response.status_code == expected_status
#     assert expected_error in response.json()["detail"]
