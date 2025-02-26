import pytest
import requests
import time
from app.database import db

# Base API URLs
BASE_URL = "http://localhost:8000/api/users"
SIGNIN_URL = "http://localhost:8000/auth/signin"
REGISTER_URL = "http://localhost:8000/api/users"

# Test Users
TEST_USERS = [
    {"name": "User One", "email": "user1@example.com", "password": "Password123!", "role": "admin"},
    {"name": "User Two", "email": "user2@example.com", "password": "Password123!"},
    {"name": "User Three", "email": "user3@example.com", "password": "Password123!"},
]

# Store Authentication Token
TOKEN = ""

# Setup: Register users and obtain JWT token
@pytest.fixture(scope="module", autouse=True)
def setup_users():
    global TOKEN
    # Create test users
    for user in TEST_USERS:
        requests.post(REGISTER_URL, json=user)

    # Authenticate and get a JWT token
    response = requests.post(SIGNIN_URL, json={"email": TEST_USERS[0]["email"], "password": TEST_USERS[0]["password"]})
    assert response.status_code == 200
    TOKEN = response.json()["access_token"]

    yield  # Run tests

    # Cleanup test users directly from MongoDB
    db.users.delete_many({})  # Deletes all test users


# POSITIVE TEST CASES
@pytest.mark.parametrize("query_params, expected_status", [
    ("", 200),  # Fetch all users
    ("?page=1&limit=10", 200),  # Pagination (First Page)
    ("?page=2&limit=10", 200),  # Pagination (Second Page)
    ("?limit=100", 200),  # Large request
])
def test_list_users_positive(query_params, expected_status):
    """Tests user listing with valid parameters."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}{query_params}", headers=headers)
    print(response.json())
    assert response.status_code == expected_status
    assert isinstance(response.json(), list)


# NEGATIVE TEST CASES
@pytest.mark.parametrize("query_params, expected_status, expected_error,", [
    ("", 401, "Not authenticated"),  # No Token
    ("", 401, "Invalid token"),  # Expired/Invalid Token
])
def test_list_users_negative(query_params, expected_status, expected_error):
    """Tests user listing with invalid inputs."""
    headers = {"Authorization": "Bearer " if "Invalid token" not in expected_error else "Bearer invalid_token"}
    response = requests.get(f"{BASE_URL}{query_params}", headers=headers)
    print(response.json())
    assert response.status_code == expected_status
    assert expected_error in response.json()["detail"]

# NEGATIVE TEST CASES WITH INVALID QUERIES
@pytest.mark.parametrize("query_params, expected_status, expected_error,", [
    ("?page=-1&limit=10", 422, 'Input should be greater than or equal to 1'),  # Negative Page Number
    ("?page=1&limit=0", 422, 'Input should be greater than or equal to 1'),  # Zero Limit
    ("?page=abc&limit=xyz", 422, 'Input should be a valid integer, unable to parse string as an integer'),  # Non-Numeric Input
])
def test_list_users_negative_with_invalid_queries(query_params, expected_status, expected_error):
    """Tests user listing with invalid inputs."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}{query_params}", headers=headers)
    print(response.json())
    assert response.status_code == expected_status
    error_messages = [error["msg"] for error in response.json()["detail"]]

    # Ensure expected error message is in the response
    assert expected_error in error_messages


# EDGE TEST CASES
@pytest.mark.parametrize("query_params, expected_status", [
    ("?limit=1", 200),  # Minimum Limit
    ("?limit=1000", 200),  # Exceeding Limit (Should return max allowed)
    ("?page=9999&limit=10", 200),  # High Page Number (Should return empty)
    ("?page= 1 &limit= 10 ", 200),  # Query Params with Spaces
])
def test_list_users_edge_cases(query_params, expected_status):
    """Tests user listing at boundary conditions."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}{query_params}", headers=headers)
    assert response.status_code == expected_status

# SECURITY TEST CASES
@pytest.mark.parametrize("query_params, expected_status", [
    ("?page=1 OR 1=1", 422),  # SQL Injection Attempt
    ("?page=<script>alert('Hacked!')</script>&limit=10", 422),  # XSS Attack
])
def test_list_users_security(query_params, expected_status):
    """Tests user listing against security vulnerabilities."""
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.get(f"{BASE_URL}{query_params}", headers=headers)
    assert response.status_code == expected_status


# def test_brute_force_protection():
#     """Simulates brute force attack and checks rate limiting."""
#     headers = {"Authorization": f"Bearer {TOKEN}"}
#     max_attempts = 10  # Adjust based on rate limit settings

#     for _ in range(max_attempts):
#         requests.get(BASE_URL, headers=headers)

#     # After multiple requests, should return HTTP 429
#     response = requests.get(BASE_URL, headers=headers)
#     assert response.status_code == 429


# def test_revoked_token():
#     """Tests access with a revoked JWT token."""
#     headers = {"Authorization": "Bearer revoked_token"}
#     response = requests.get(BASE_URL, headers=headers)
#     assert response.status_code == 401
#     assert "Invalid token" in response.json()["detail"]
