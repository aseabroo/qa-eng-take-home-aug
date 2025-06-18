# Pytest suite to validate the QA take-home FastAPI platform via API testing
import httpx
import pytest

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="session", autouse=True)
def force_seed_data():
    """Reseed the database once before all tests."""
    resp = httpx.post(f"{BASE_URL}/seed-data")
    assert resp.status_code == 200, f"Seeding failed: {resp.status_code} – {resp.text}"

def test_print_all_users():
    token = get_token_for_user("admin@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/api/v1/users/", headers=headers)
    print("Users:", response.status_code, response.json())
    assert response.status_code == 200
    

@pytest.mark.users
def test_debug_list_users():
    token = get_token_for_user("admin@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    resp = httpx.get(f"{BASE_URL}/api/v1/users/", headers=headers)
    print("Users:", resp.json())

# ---------- Optional Utility for Auth ----------
def get_token_for_user(username, password):
    # This function retrieves a JWT token for a given user by logging in.
    payload = {"username": username, "password": password}
    response = httpx.post(f"{BASE_URL}/api/v1/auth/login", data=payload)
    assert response.status_code == 200
    return response.json()["access_token"]

# ---------- DEFAULT ROUTE TESTS ----------
@pytest.mark.default
def test_root_route():  # SC-DEF-001
    response = httpx.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert isinstance(response.text, str)

@pytest.mark.default
def test_health_check():  # SC-DEF-002
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert "healthy" in response.text.lower() or response.json()

@pytest.mark.default
def test_login_route_accessible():  # SC-DEF-003
    response = httpx.get(f"{BASE_URL}/login")
    assert response.status_code == 200

@pytest.mark.default
def test_dashboard_authenticated():  # SC-DEF-004
    token = get_token_for_user("john@example.com", "user123")
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/dashboard", headers=headers)
    assert response.status_code == 200

@pytest.mark.default
def test_dashboard_unauthenticated():  # SC-DEF-005
    response = httpx.get(f"{BASE_URL}/dashboard")
    assert response.status_code == 200
    assert "<title>Dashboard" in response.text 

@pytest.mark.default
def test_admin_access():  # SC-DEF-006
    admin_token = get_token_for_user("admin@example.com", "admin123")
    user_token = get_token_for_user("john@example.com", "user123")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_headers = {"Authorization": f"Bearer {user_token}"}

    admin_response = httpx.get(f"{BASE_URL}/admin", headers=admin_headers)
    user_response = httpx.get(f"{BASE_URL}/admin", headers=user_headers)

    assert admin_response.status_code == 200

    # Note: Regular users currently receive 200 OK too.
    # This may indicate missing RBAC enforcement on the backend.
    # If RBAC is implemented later, update this to:
    # assert user_response.status_code == 403
    assert user_response.status_code == 200
    assert "<script>" in user_response.text or "window.location.href" in user_response.text

@pytest.mark.default
def test_seed_data_endpoint():  # SC-DEF-007
    response = httpx.post(f"{BASE_URL}/seed-data")
    assert response.status_code in [200, 201]

@pytest.mark.default
def test_nonexistent_route_404():  # SC-DEF-008
    response = httpx.get(f"{BASE_URL}/nonexistent")
    assert response.status_code == 404


# ---------- AUTHENTICATION TESTS ----------
@pytest.mark.auth
def test_valid_login_returns_token():  # TC-AUTH-001 / SC-AUTH-009
    data = {"username": "admin@example.com", "password": "admin123"}
    response = httpx.post(f"{BASE_URL}/api/v1/auth/login", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.auth
def test_login_wrong_password_returns_401():  # TC-AUTH-002 / SC-AUTH-010
    data = {"username": "admin@example.com", "password": "wrongpass"}
    response = httpx.post(f"{BASE_URL}/api/v1/auth/login", data=data)
    assert response.status_code == 401

@pytest.mark.auth
def test_login_empty_fields_returns_422():  # TC-AUTH-003 / SC-AUTH-011
    data = {"username": "", "password": ""}
    response = httpx.post(f"{BASE_URL}/api/v1/auth/login", data=data)
    assert response.status_code == 422

@pytest.mark.auth
def test_login_malformed_json_returns_400():  # TC-AUTH-004 / SC-AUTH-012
    malformed_payload = "username=admin&password=admin123"  # not valid JSON
    headers = {"Content-Type": "application/json"}
    response = httpx.post(f"{BASE_URL}/api/v1/auth/login", content=malformed_payload, headers=headers)
    assert response.status_code in [400, 422, 433]  # based on backend handling

@pytest.mark.auth
def test_auth_me_returns_user_info():  # TC-AUTH-005 / SC-AUTH-013
    login_resp = httpx.post(f"{BASE_URL}/api/v1/auth/login", data={"username": "admin@example.com", "password": "admin123"})
    token = login_resp.json()["access_token"]
     #debug assertions here
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    assert "access_token" in login_resp.json(), f"No token returned: {login_resp.json()}"
    
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert "email" in response.json()

@pytest.mark.auth
def test_auth_me_without_token_returns_401():  # TC-AUTH-006 / SC-AUTH-014
    response = httpx.get(f"{BASE_URL}/api/v1/auth/me")
    assert response.status_code == 403
    assert response.json() ["detail"].lower() == "not authenticated"

@pytest.mark.auth
def test_protected_with_fake_token_returns_403():  # TC-AUTH-007 / SC-AUTH-015
    headers = {"Authorization": "Bearer faketoken.abc.def"}
    response = httpx.get(f"{BASE_URL}/api/v1/auth/protected", headers=headers)
    assert response.status_code in [401, 403]

@pytest.mark.auth
def test_regular_user_access_admin_only_returns_403():  # TC-AUTH-008 / SC-AUTH-016
    login_resp = httpx.post(f"{BASE_URL}/api/v1/auth/login", data={"username": "john@example.com", "password": "user123"})
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/api/v1/auth/admin-only", headers=headers)
    assert response.status_code == 403

# ---------- USER MANAGEMENT TESTS ----------
@pytest.mark.users
def test_admin_can_create_user():  # TC-USR-001 / SC-USR-017
    token = get_token_for_user("admin@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"email": "newuser@example.com", "name": "New User", "password": "secure123", "role": "admin"}
    response = httpx.post(f"{BASE_URL}/api/v1/users/", headers=headers, json=payload)
    assert response.status_code in [200, 201]
    assert response.json()["email"] == "newuser@example.com"
    assert response.json()["role"] == "admin"


@pytest.mark.users
@pytest.mark.xfail(reason="BUG-003: Regular users should not be able to create users - RBAC missing")
def test_regular_user_cannot_create_user():  # TC-USR-002 / SC-USR-018
    token = get_token_for_user("john@example.com", "user123")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"email": "shouldfail@example.com", "name": "Should Fail", "password": "test123", "role": "regular"}
    
    response = httpx.post(f"{BASE_URL}/api/v1/users/", headers=headers, json=payload)
    
    # Cleanup the created user (if status != 403)
    if response.status_code == 201:
        created_user_id = response.json().get("id")
        admin_token = get_token_for_user("admin@example.com", "admin123")
        admin_headers = {"Authorization" : f"Bearer {admin_token}"}
        httpx.delete(f"{BASE_URL}/api/v1/users/{created_user_id}", headers=admin_headers)
    # This test is currently failing because the backend allows this behavior
    assert response.status_code == 403, (
        f"Expected 403, got {response.status_code} with message: {response.text} - regular users should not create users"
    )


@pytest.mark.users
def test_admin_can_list_users():  # TC-USR-003 / SC-USR-019
    token = get_token_for_user("admin@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/api/v1/users/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.users
@pytest.mark.xfail(reason="BUG-004: Regular users should not be able to list users (RBAC)")
def test_regular_user_cannot_list_users():  # TC-USR-004 / SC-USR-020
    token = get_token_for_user("john@example.com", "user123")
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/api/v1/users/", headers=headers)
    assert response.status_code in [401, 403], f"Expected 403 or 401, got {response.status_code}"


@pytest.mark.users
def test_admin_can_get_user_by_id():  # TC-USR-005 / SC-USR-021
    token = get_token_for_user("admin@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/api/v1/users/2", headers=headers)  # assuming ID=2 exists
    assert response.status_code == 200


@pytest.mark.users
@pytest.mark.xfail(reason="BUG-005: Regular users should not be able to get other users (RBAC)")    
def test_regular_user_cannot_get_other_user():  # TC-USR-006 / SC-USR-022
    token = get_token_for_user("john@example.com", "user123")
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.get(f"{BASE_URL}/api/v1/users/1", headers=headers)  # assuming ID=1 is not them
    print("Response body:", response.text)  # Debugging output
    assert response.status_code in [401, 403], f"Expected 403 or 401, got {response.status_code} - regular users should not access other users"


@pytest.mark.users
def test_admin_can_update_user():  # TC-USR-007 / SC-USR-023
    token = get_token_for_user("admin@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Create a throwaway user for update testing
    create_payload = {
        "email" : "update-test@example.com",
        "name" : "Temp Update Target",
        "password" : "temppass123",
        "role" : "regular"
    }
    create_resp = httpx.post(f"{BASE_URL}/api/v1/users/", headers=headers, json=create_payload)
    assert create_resp.status_code in [200, 201], f"User creation failed: {create_resp.status_code} - {create_resp.text}"
    user = create_resp.json()
    user_id = user["id"]
    version = user["version"]

    # Step 2: Update the created user
    update_payload = {
        "email" : "updateduser@example.com",
        "name" : "Updated User",
        "passoword" : "temppass123",  # Note: Password is not updated here, just for testing    
        "role" : "regular",
        "is_active" : True,
        "version" : version
    }
    update_resp = httpx.put(f"{BASE_URL}/api/v1/users/{user_id}", headers=headers, json=update_payload)
    print("Update response:", update_resp.status_code, update_resp.text)
    assert update_resp.status_code == 200, f"Expected 200 OK, got {update_resp.status_code} - {update_resp.text}"
    
    updated = update_resp.json()
    assert updated["email"] == "updateduser@example.com"
    assert updated["name"] == "Updated User"
    assert updated["role"] == "regular"

    # Step 3: Cleanup - delete the created user
    delete_resp = httpx.delete(f"{BASE_URL}/api/v1/users/{user_id}", headers=headers)   
    assert delete_resp.status_code in [200, 204], f"Cleanup failed: {delete_resp.status_code} - {delete_resp.text}"
     
@pytest.mark.users
@pytest.mark.xfail(reason="BUG-008: Unauthorized update returns 500 instead of 403 – RBAC missing or not guarded")
def test_regular_user_cannot_update_user():  # TC-USR-008 / SC-USR-024
    token = get_token_for_user("john@example.com", "user123")
    admin_token = get_token_for_user("admin@example.com", "admin123")

    # Get the real version of user 1
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    user_resp = httpx.get(f"{BASE_URL}/api/v1/users/1", headers=admin_headers)
    assert user_resp.status_code == 200
    current_version = user_resp.json()["version"]

    # Attempt unauthorized update
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "email": "shouldfail@example.com",
        "name": "Unauthorized Attempt",
        "role": "regular",
        "is_active": True,
        "version": current_version
    }
    response = httpx.put(f"{BASE_URL}/api/v1/users/1", headers=headers, json=payload)

    # TEMP workaround to avoid crashing the test suite
    if response.status_code == 500:
        pytest.xfail(f"Backend threw 500 error: {response.text}")

    assert response.status_code == 403, f"Expected 403 Forbidden, got {response.status_code} - {response.text}"

@pytest.mark.users
def test_admin_can_delete_user():  # TC-USR-009 / SC-USR-025
    token = get_token_for_user("admin@example.com", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    # Create disposable user
    payload = {
        "email" : "delete-test@example.com",
        "name" : "Delete Me",
        "password" : "delete123",
        "role" : "regular"
    }
    create_resp = httpx.post(f"{BASE_URL}/api/v1/users/", headers=headers, json=payload)
    assert create_resp.status_code in [200, 201]
    user_id = create_resp.json()["id"]

    # Delete the disposable user
    delete_resp = httpx.delete(f"{BASE_URL}/api/v1/users/{user_id}", headers=headers)
    assert delete_resp.status_code in [200, 204]



@pytest.mark.users
@pytest.mark.xfail(reason="BUG-007 : Regular users can delete users - missing RBAC")
def test_regular_user_cannot_delete_user():  # TC-USR-010 / SC-USR-026
    token = get_token_for_user("john@example.com", "user123")
    headers = {"Authorization": f"Bearer {token}"}
    response = httpx.delete(f"{BASE_URL}/api/v1/users/1", headers=headers)
    assert response.status_code == 403