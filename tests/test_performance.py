import pytest
from tests.conftest import client, auth_headers

@pytest.mark.benchmark
def test_create_product_performance(client, auth_headers, benchmark):
    \"\"\"Benchmark product creation performance.\"\"\"
    product_data = {
        "name": "Performance Test Product",
        "description": "This is a test product for performance testing",
        "price": 99.99,
        "stock": 10
    }
    
    def create_product():
        client.post("/products", json=product_data, headers=auth_headers)
    
    result = benchmark(create_product)
    print(f"Performance: {result}")

@pytest.mark.benchmark
def test_list_products_performance(client, auth_headers, benchmark):
    \"\"\"Benchmark product listing performance.\"\"\"
    # Create some products first
    for i in range(10):
        product_data = {
            "name": f"Product {i}",
            "description": f"Test product {i}",
            "price": 99.99,
            "stock": 10
        }
        client.post("/products", json=product_data, headers=auth_headers)
    
    def list_products():
        client.get("/products", headers=auth_headers)
    
    result = benchmark(list_products)
    print(f"Performance: {result}")
