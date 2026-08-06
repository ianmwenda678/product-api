import pytest
from tests.conftest import client, test_user, auth_headers

def test_create_product(client, auth_headers):
    \"\"\"Test creating a product.\"\"\"
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    response = client.post("/products", json=product_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]

def test_list_products(client, auth_headers):
    \"\"\"Test listing products.\"\"\"
    # Create a product first
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    client.post("/products", json=product_data, headers=auth_headers)
    
    # List products
    response = client.get("/products", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_get_product(client, auth_headers):
    \"\"\"Test getting a single product.\"\"\"
    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    create_response = client.post("/products", json=product_data, headers=auth_headers)
    product_id = create_response.json()["id"]
    
    # Get the product
    response = client.get(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == product_data["name"]

def test_get_product_not_found(client, auth_headers):
    \"\"\"Test getting a non-existent product.\"\"\"
    response = client.get("/products/99999", headers=auth_headers)
    assert response.status_code == 404

def test_update_product(client, auth_headers):
    \"\"\"Test updating a product.\"\"\"
    # Create a product
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    create_response = client.post("/products", json=product_data, headers=auth_headers)
    product_id = create_response.json()["id"]
    
    # Update the product
    update_data = {
        "name": "Updated Product",
        "price": 149.99
    }
    response = client.patch(f"/products/{product_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

def test_delete_product(client, admin_auth_headers):
    \"\"\"Test deleting a product (admin only).\"\"\"
    # Create a product first (as admin)
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    create_response = client.post("/products", json=product_data, headers=admin_auth_headers)
    product_id = create_response.json()["id"]
    
    # Delete the product
    response = client.delete(f"/products/{product_id}", headers=admin_auth_headers)
    assert response.status_code == 204
    
    # Verify deletion
    response = client.get(f"/products/{product_id}", headers=admin_auth_headers)
    assert response.status_code == 404
