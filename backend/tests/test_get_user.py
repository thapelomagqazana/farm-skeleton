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
    {"name": "Jane Doe", "email": "jane@example.com", "password": "Password123!"},
    {"name": "User Test", "email": "user+test@example.com", "password": "Password123!"},
]

# Store authentication token and user IDs
TOKEN = ""
USER_IDS = {}

# Setup: Register users, get their IDs and JWT token
@pytest.fixture(scope="module", autouse=True)
def setup_users():
    global TOKEN, USER_IDS

    # Create test users
    for user in TEST_USERS:
        response = requests.post(REGISTER_URL, json=user)
        if response.status_code == 201:
            user_id = response.json()["id"]
            USER_IDS[user["email"]] = user_id

    # Authenticate and get a JWT token
    response = requests.post(SIGNIN_URL, json={"email": TEST_USERS[0]["email"], "password": TEST_USERS[0]["password"]})
    assert response.status_code == 200
    TOKEN = response.json()["access_token"]

    yield  # Run tests

    # Cleanup test users directly from MongoDB
    db.users.delete_many({})  # Deletes all test users


# POSITIVE TEST CASES
@pytest.mark.parametrize("email, expected_status", [
    ("john@example.com", 200),  # Fetch an existing user
    ("jane@example.com", 200),  # Fetch user immediately after creation
    ("user+test@example.com", 200),  # Fetch user with special characters in email
])
def test_get_user_positive(email, expected_status):
    """Tests fetching an existing user by ID."""
    user_id = USER_IDS[email]
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/{user_id}", headers=headers)

    assert response.status_code == expected_status
    assert response.json()["id"] == user_id
    assert response.json()["email"] == email


# NEGATIVE TEST CASES
@pytest.mark.parametrize("user_id, expected_status, expected_error", [
    # ("non_existent_id", 404, "User not found"),  # Non-existent user
    ("invalid123", 400, "Invalid user ID format"),  # Invalid user ID format
])
def test_get_user_negative(user_id, expected_status, expected_error):
    """Tests fetching a user with invalid inputs."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/{user_id}", headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# AUTHENTICATION TEST CASES
@pytest.mark.parametrize("auth_header, expected_status, expected_error", [
    (None, 401, "Not authenticated"),  # No authentication
    ("Bearer expired_token", 401, "Invalid token"),  # Expired JWT token
    ("Bearer invalid_token", 401, "Invalid token"),  # Invalid JWT token
])
def test_get_user_auth(auth_header, expected_status, expected_error):
    """Tests fetching a user with authentication errors."""
    headers = {"Authorization": auth_header} if auth_header else {}
    user_id = list(USER_IDS.values())[0]  # Get any valid user ID
    response = requests.get(f"{BASE_URL}/{user_id}", headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# EDGE TEST CASES
@pytest.mark.parametrize("user_id, expected_status, expected_error", [
    ("1", 400, "Invalid user ID format"),  # Very short ID
    ("x" * 256, 400, "Invalid user ID format"),  # Very long ID
    (" valid_id ", 400, "Invalid user ID format"),  # Leading/trailing spaces
    # ("VALIDID", 404, "User not found"),  # Upper-case ID
])
def test_get_user_edge_cases(user_id, expected_status, expected_error):
    """Tests fetching a user at boundary conditions."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/{user_id}", headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# SECURITY TEST CASES
@pytest.mark.parametrize("user_id, expected_status, expected_error", [
    ("' OR 1=1 --", 400, "Invalid user ID format"),  # SQL Injection Attempt
    # ("<script>alert('Hacked!')</script>", 400, "Invalid user ID format"),  # XSS Attack
])
def test_get_user_security(user_id, expected_status, expected_error):
    """Tests fetching a user against security vulnerabilities."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}/{user_id}", headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


# def test_brute_force_protection():
#     """Simulates brute force attack and checks rate limiting."""
#     headers = {"Authorization": f"Bearer {TOKEN}"}
#     user_id = list(USER_IDS.values())[0]  # Get any valid user ID
#     max_attempts = 10  # Adjust based on rate limit settings

#     for _ in range(max_attempts):
#         requests.get(f"{BASE_URL}/{user_id}", headers=headers)

#     # After multiple requests, should return HTTP 429
#     response = requests.get(f"{BASE_URL}/{user_id}", headers=headers)
#     assert response.status_code == 429


# def test_revoked_token():
#     """Tests access with a revoked JWT token."""
#     headers = {"Authorization": "Bearer revoked_token"}
#     user_id = list(USER_IDS.values())[0]
#     response = requests.get(f"{BASE_URL}/{user_id}", headers=headers)

#     assert response.status_code == 401
#     assert "Invalid token" in response.json()["detail"]
