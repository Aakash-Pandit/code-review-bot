from unittest.mock import patch


def test_stream_requires_auth(client):
    response = client.post("/stream", json={"query": "hello"})
    assert response.status_code == 401


def test_stream_invalid_token_returns_401(client):
    response = client.post(
        "/stream",
        json={"query": "hello"},
        headers={"Authorization": "Bearer badtoken"},
    )
    assert response.status_code == 401


def test_stream_happy_path(client, auth_headers, mock_ollama_stream):
    mock_cm, _ = mock_ollama_stream(chunks=("chunk1 ", "chunk2"))
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post("/stream", json={"query": "what is python?"}, headers=auth_headers)
    assert response.status_code == 200
    assert "chunk1 " in response.text
    assert "chunk2" in response.text


def test_stream_passes_query_as_prompt(client, auth_headers, mock_ollama_stream):
    mock_cm, mock_client = mock_ollama_stream()
    query = "explain recursion to me"
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        client.post("/stream", json={"query": query}, headers=auth_headers)
    call_kwargs = mock_client.stream.call_args
    assert call_kwargs.kwargs["json"]["prompt"] == query
    assert call_kwargs.kwargs["json"]["stream"] is True


def test_stream_missing_query_returns_422(client, auth_headers):
    response = client.post("/stream", json={}, headers=auth_headers)
    assert response.status_code == 422
