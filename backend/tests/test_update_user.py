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
@pytest.mark.parametrize("update_data, expected_status", [
    ({"name": "New Name"}, 200),  # TC-01: Update name only
    ({"email": "newemail@example.com"}, 200),  # TC-02: Update email only
    ({"role": "admin"}, 200),  # TC-03: Update role to admin
    ({"password": "NewPass@123"}, 200),  # TC-04: Update password
    ({"name": "New User", "email": "new@example.com", "password": "Pass@123"}, 200),  # TC-05: Multiple updates
])
def test_update_user_positive(update_data, expected_status):
    """Tests updating a user with valid data."""
    user_id = list(USER_IDS.values())[0]  # Get a valid user ID
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.put(f"{BASE_URL}/{user_id}", json=update_data, headers=headers)
    print(response)

    assert response.status_code == expected_status
    if "message" not in response.json():
        assert response.json()["id"] == user_id  # Ensure user ID remains the same


# NEGATIVE TEST CASES
@pytest.mark.parametrize("user_id, update_data, expected_status, expected_error", [
    # ("non_existent_id", {"name": "Random Name"}, 404, "User not found"),  # TC-06: Non-existent user
    ("invalid123", {"name": "New Name"}, 400, "Invalid user ID format"),  # TC-07: Invalid user ID
    # ("valid_id", {"password": "123"}, 422, "Password must be at least 6 characters"),  # TC-09: Short password
    # ("valid_id", {"name": ""}, 422, "Name must contain characters"),  # TC-10: Blank name
    # ("valid_id", {"name": "<script>alert('XSS')</script>"}, 422, "Invalid characters in name"),  # TC-11: XSS Attack
])
def test_update_user_negative(user_id, update_data, expected_status, expected_error):
    """Tests updating a user with invalid inputs."""
    user_id = list(USER_IDS.values())[0] if user_id == "valid_id" else user_id
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.put(f"{BASE_URL}/{user_id}", json=update_data, headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]

# NEGATIVE TEST CASES WITH INVALID REQUESTS
@pytest.mark.parametrize("user_id, update_data, expected_status, expected_error", [
    ("valid_id", {"password": "123"}, 422, 'Value error, Password must include letters, numbers, and special characters'),  # TC-09: Short password
    ("valid_id", {"name": ""}, 422, 'Value error, Name must contain characters'),  # TC-10: Blank name
    ("valid_id", {"name": "<script>alert('XSS')</script>"}, 422, 'Value error, Invalid characters in name'),  # TC-11: XSS Attack
    ("valid_id", {"email": "invalid-email"}, 422, 'value is not a valid email address: An email address must have an @-sign.'),  # TC-08: Invalid email format
    ("valid_id", {"name": "<script>alert('Hacked!')</script>"}, 422, 'Value error, Invalid characters in name'),  # TC-23: XSS Attack
])
def test_update_user_negative(user_id, update_data, expected_status, expected_error):
    """Tests updating a user with invalid inputs."""
    user_id = list(USER_IDS.values())[0] if user_id == "valid_id" else user_id
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.put(f"{BASE_URL}/{user_id}", json=update_data, headers=headers)

    assert response.status_code == expected_status
    error_messages = [error["msg"] for error in response.json()["detail"]]

    # Ensure expected error message is in the response
    assert expected_error in error_messages



# EDGE TEST CASES
@pytest.mark.parametrize("user_id, update_data, expected_status, expected_error", [
    ("1", {"name": "User"}, 400, "Invalid user ID format"),  # TC-16: Very short ID
    ("x" * 256, {"name": "User"}, 400, "Invalid user ID format"),  # TC-17: Very long ID
    ("valid_id", {"name": "a" * 255}, 200, None),  # TC-18: Max limit name (should succeed)
    ("valid_id", {"name": "a" * 256}, 422, "Name cannot exceed 255 characters"),  # TC-19: Name too long
    ("valid_id", {"email": "TEST@EXAMPLE.COM"}, 200, None),  # TC-20: Normalize email
    ("valid_id", {"role": " admin "}, 200, None),  # TC-21: Trimmed role
])
def test_update_user_edge_cases(user_id, update_data, expected_status, expected_error):
    """Tests updating a user at boundary conditions."""
    user_id = list(USER_IDS.values())[0] if user_id == "valid_id" else user_id
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.put(f"{BASE_URL}/{user_id}", json=update_data, headers=headers)

    assert response.status_code == expected_status
    if expected_error:
        assert expected_error in response.json()["detail"]


# SECURITY TEST CASES
@pytest.mark.parametrize("user_id, update_data, expected_status, expected_error", [
    ("valid_id", {"name": "' OR 1=1 --"}, 400, "Invalid characters in name"),  # TC-22: SQL Injection
])
def test_update_user_security(user_id, update_data, expected_status, expected_error):
    """Tests updating a user against security vulnerabilities."""
    user_id = list(USER_IDS.values())[0]
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.put(f"{BASE_URL}/{user_id}", json=update_data, headers=headers)

    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]


