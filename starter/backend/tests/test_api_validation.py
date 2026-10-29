import pytest
from backend.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

def test_add_order_api_missing_field_returns_400(client):
    response = client.post('/api/orders', json={"item_name": "Laptop", "quantity": 1, "customer_id": "C1"})
    assert response.status_code == 400
    assert "order_id" in response.json['error']

def test_add_order_api_without_json_body_returns_400(client):
    response = client.post('/api/orders', data="not json", content_type='text/plain')
    assert response.status_code == 400
    assert 'error' in response.json

def test_add_order_api_invalid_status_returns_400(client):
    response = client.post('/api/orders', json={
        "order_id": "BAD001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "lost"
    })
    assert response.status_code == 400
    assert client.get('/api/orders/BAD001').status_code == 404

def test_update_order_status_api_missing_new_status_returns_400(client):
    client.post('/api/orders', json={"order_id": "UPD001", "item_name": "A", "quantity": 1, "customer_id": "C1"})
    response = client.put('/api/orders/UPD001/status', json={})
    assert response.status_code == 400
    assert "new_status" in response.json['error']

def test_update_order_status_api_without_json_body_returns_400(client):
    client.post('/api/orders', json={"order_id": "UPD002", "item_name": "A", "quantity": 1, "customer_id": "C1"})
    response = client.put('/api/orders/UPD002/status', data="not json", content_type='text/plain')
    assert response.status_code == 400

def test_update_order_status_api_invalid_status_returns_400(client):
    client.post('/api/orders', json={"order_id": "UPD003", "item_name": "A", "quantity": 1, "customer_id": "C1"})
    response = client.put('/api/orders/UPD003/status', json={"new_status": "lost"})
    assert response.status_code == 400
    assert client.get('/api/orders/UPD003').json['status'] == "pending"

def test_update_order_status_api_not_found_returns_404(client):
    response = client.put('/api/orders/NONEXISTENT/status', json={"new_status": "shipped"})
    assert response.status_code == 404
