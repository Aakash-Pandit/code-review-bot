def test_health_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body(client):
    response = client.get("/health")
    assert response.json() == {"status": "healthy"}


def test_health_no_auth_required(client):
    response = client.get("/health")
    assert response.status_code == 200
