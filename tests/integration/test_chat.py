from unittest.mock import patch


def test_chat_requires_auth(client):
    response = client.post("/chat", json={"query": "hello"})
    assert response.status_code == 401


def test_chat_invalid_token_returns_401(client):
    response = client.post(
        "/chat",
        json={"query": "hello"},
        headers={"Authorization": "Bearer badtoken"},
    )
    assert response.status_code == 401


def test_chat_happy_path(client, auth_headers, mock_ollama_chat):
    mock_cm, _ = mock_ollama_chat(answer="42 is the answer")
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post("/chat", json={"query": "what is the answer?"}, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "query" in body
    assert "answer" in body


def test_chat_answer_comes_from_ollama_response(client, auth_headers, mock_ollama_chat):
    mock_cm, _ = mock_ollama_chat(answer="Paris is the capital of France")
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post("/chat", json={"query": "capital of France?"}, headers=auth_headers)
    assert response.json()["answer"] == "Paris is the capital of France"


def test_chat_query_echoed_in_response(client, auth_headers, mock_ollama_chat):
    query = "what is 2+2?"
    mock_cm, _ = mock_ollama_chat()
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post("/chat", json={"query": query}, headers=auth_headers)
    assert response.json()["query"] == query


def test_chat_ollama_error_propagates_status_code(client, auth_headers, mock_ollama_chat):
    mock_cm, _ = mock_ollama_chat(answer="Service Unavailable", status_code=503)
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/chat",
            json={"query": "hello"},
            headers=auth_headers,
        )
    assert response.status_code == 503


def test_chat_missing_query_returns_422(client, auth_headers):
    response = client.post("/chat", json={}, headers=auth_headers)
    assert response.status_code == 422
