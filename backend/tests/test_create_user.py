import pytest
import requests
import string
import random
from app.database import db

# Base API URL
BASE_URL = "http://localhost:8000/api/users"

# Generate a unique email to avoid duplicate issues
def generate_unique_email():
    return "testuser@example.com"

# Generate a long string (for boundary tests)
def generate_long_string(length):
    return ''.join(random.choices(string.ascii_letters, k=length))

@pytest.fixture(scope="function", autouse=True)
def cleanup():    
    """Ensures test environment is clean before and after tests."""
    yield
    # Cleanup test users directly from MongoDB
    db.users.delete_many({})  # Deletes all test users


# POSITIVE TEST CASES
@pytest.mark.parametrize("payload, expected_status", [
    ({"name": "John Doe", "email": generate_unique_email(), "password": "StrongPass123%"}, 201),
    ({"name": "J", "email": generate_unique_email(), "password": "Pass1234%"}, 201),
    ({"name": generate_long_string(255), "email": generate_unique_email(), "password": "SecurePass1!"}, 201),
    ({"name": "SecureUser", "email": generate_unique_email(), "password": "Very$tr0ngP@ssword123"}, 201),
    ({"name": "DomainUser", "email": "user@sub.example.co.uk", "password": "Pass1234%"}, 201),
])
def test_create_user_positive(payload, expected_status):
    """Tests user creation with valid data"""
    response = requests.post(BASE_URL, json=payload)
    print(response.json())

    assert response.status_code == expected_status
    assert "id" in response.json()

# NEGATIVE TEST CASES
@pytest.mark.parametrize("payload, expected_status, expected_error", [
    ({"email": "missingname@example.com", "password": "Pass1234%"}, 422, "Field required"),
    ({"name": "NoEmail", "password": "Pass1234%"}, 422, "Field required"),
    ({"name": "NoPassword", "email": "nopass@example.com"}, 422, "Field required"),
    ({"name": "InvalidEmail", "email": "invalid-email", "password": "Pass1234%"}, 422, 'value is not a valid email address: An email address must have an @-sign.'),
    ({"name": "ShortPass", "email": generate_unique_email(), "password": "123"}, 422, 'String should have at least 6 characters'),
    ({"name": "LongPass", "email": generate_unique_email(), "password": generate_long_string(129)}, 422, 'String should have at most 128 characters'),
    ({"name": "WeakPass", "email": generate_unique_email(), "password": "password"}, 422, 'Value error, Password must include letters, numbers, and special characters'),
])
def test_create_user_negative(payload, expected_status, expected_error):
    """Tests user creation with invalid data"""
    response = requests.post(BASE_URL, json=payload)

    assert response.status_code == expected_status
     # Extract error messages from response
    error_messages = [error["msg"] for error in response.json()["detail"]]

    # Ensure expected error message is in the response
    assert expected_error in error_messages

# EDGE TEST CASES
@pytest.mark.parametrize("payload, expected_status, expected_error", [
    ({"name": "", "email": generate_unique_email(), "password": "Pass1234%"}, 422, 'String should have at least 1 character'),
    ({"name": "User", "email": "", "password": "Pass1234%"}, 422, 'value is not a valid email address: An email address must have an @-sign.'),
    ({"name": "User", "email": generate_unique_email(), "password": ""}, 422, 'String should have at least 6 characters'),
    ({"name": "   ", "email": generate_unique_email(), "password": "Pass1234%"}, 422, 'Value error, Name must contain characters'),
    ({"name": "User", "email": generate_unique_email(), "password": "     "}, 422, 'String should have at least 6 characters'),
    ({"name": generate_long_string(256), "email": generate_unique_email(), "password": "SecurePass1!"}, 422, 'String should have at most 255 characters'),
])
def test_create_user_edge_cases(payload, expected_status, expected_error):
    """Tests user creation at boundary conditions"""
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == expected_status
    error_messages = [error["msg"] for error in response.json()["detail"]]

    # Ensure expected error message is in the response
    assert expected_error in error_messages

# SECURITY TEST CASES
@pytest.mark.parametrize("payload, expected_status", [
    ({"name": "admin", "email": "admin' OR '1'='1", "password": "Pass1234%"}, 422),
    ({"name": "<script>alert('XSS')</script>", "email": "xss@example.com", "password": "Pass1234%"}, 422),
    ({"name": generate_long_string(10000), "email": "largepayload@example.com", "password": "Pass1234%"}, 422),
])
def test_create_user_security(payload, expected_status):
    """Tests user creation against security vulnerabilities"""
    response = requests.post(BASE_URL, json=payload)
    assert response.status_code == expected_status
