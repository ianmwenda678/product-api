import pytest
from tests.conftest import client, test_user

def test_full_crud_flow(client, test_user):
    \"\"\"Test the full CRUD flow from registration to deletion.\"\"\"
    # 1. Register user
    register_response = client.post("/register", json=test_user)
    assert register_response.status_code == 201
    
    # 2. Login
    login_response = client.post(
        "/login",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create a product
    product_data = {
        "name": "Integration Test Product",
        "description": "This is a test product for integration testing",
        "price": 199.99,
        "stock": 15
    }
    create_response = client.post("/products", json=product_data, headers=headers)
    assert create_response.status_code == 201
    product_id = create_response.json()["id"]
    assert create_response.json()["name"] == product_data["name"]
    
    # 4. Get the product
    get_response = client.get(f"/products/{product_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["price"] == product_data["price"]
    
    # 5. Update the product
    update_data = {"name": "Updated Integration Product", "price": 249.99}
    update_response = client.patch(f"/products/{product_id}", json=update_data, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["name"] == update_data["name"]
    assert update_response.json()["price"] == update_data["price"]
    
    # 6. List products (should include our product)
    list_response = client.get("/products", headers=headers)
    assert list_response.status_code == 200
    products = list_response.json()
    assert len(products) >= 1
    
    # 7. Delete the product (admin only)
    admin_user = {
        "username": "admin_test",
        "email": "admin_test@example.com",
        "password": "adminpass123",
        "full_name": "Admin User",
        "role": "admin"
    }
    client.post("/register", json=admin_user)
    admin_login = client.post(
        "/login",
        data={"username": admin_user["username"], "password": admin_user["password"]}
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    delete_response = client.delete(f"/products/{product_id}", headers=admin_headers)
    assert delete_response.status_code == 204
    
    # 8. Verify deletion
    verify_response = client.get(f"/products/{product_id}", headers=headers)
    assert verify_response.status_code == 404
