from unittest.mock import patch


def test_review_requires_auth(client):
    response = client.post("/review", json={"code": "x = 1"})
    assert response.status_code == 401


def test_review_invalid_token_returns_401(client):
    response = client.post(
        "/review",
        json={"code": "x = 1"},
        headers={"Authorization": "Bearer notavalidtoken"},
    )
    assert response.status_code == 401


def test_review_happy_path_full_mode(client, auth_headers, mock_ollama_stream):
    mock_cm, _ = mock_ollama_stream(chunks=("line1 ", "line2"))
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/review",
            json={"code": "x = 1", "mode": "full"},
            headers=auth_headers,
        )
    assert response.status_code == 200
    assert "line1 " in response.text
    assert "line2" in response.text


def test_review_happy_path_security_mode(client, auth_headers, mock_ollama_stream):
    mock_cm, mock_client = mock_ollama_stream()
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/review",
            json={"code": "eval(input())", "mode": "security"},
            headers=auth_headers,
        )
    assert response.status_code == 200
    call_kwargs = mock_client.stream.call_args
    assert "security vulnerabilities only" in call_kwargs.kwargs["json"]["prompt"]


def test_review_happy_path_performance_mode(client, auth_headers, mock_ollama_stream):
    mock_cm, mock_client = mock_ollama_stream()
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/review",
            json={"code": "for i in range(n): pass", "mode": "performance"},
            headers=auth_headers,
        )
    assert response.status_code == 200
    call_kwargs = mock_client.stream.call_args
    assert "performance problems only" in call_kwargs.kwargs["json"]["prompt"]


def test_review_happy_path_explain_mode(client, auth_headers, mock_ollama_stream):
    mock_cm, mock_client = mock_ollama_stream()
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/review",
            json={"code": "def foo(): return 42", "mode": "explain"},
            headers=auth_headers,
        )
    assert response.status_code == 200
    call_kwargs = mock_client.stream.call_args
    assert "Explain what this code does" in call_kwargs.kwargs["json"]["prompt"]


def test_review_default_mode_is_full(client, auth_headers, mock_ollama_stream):
    mock_cm, mock_client = mock_ollama_stream()
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/review",
            json={"code": "x = 1"},  # no mode field
            headers=auth_headers,
        )
    assert response.status_code == 200
    call_kwargs = mock_client.stream.call_args
    assert "bugs and logic errors" in call_kwargs.kwargs["json"]["prompt"]


def test_review_with_language_hint(client, auth_headers, mock_ollama_stream):
    mock_cm, mock_client = mock_ollama_stream()
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/review",
            json={"code": "x = 1", "language": "Python"},
            headers=auth_headers,
        )
    assert response.status_code == 200
    call_kwargs = mock_client.stream.call_args
    assert "The code is written in Python" in call_kwargs.kwargs["json"]["prompt"]


def test_review_without_language_no_hint(client, auth_headers, mock_ollama_stream):
    mock_cm, mock_client = mock_ollama_stream()
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/review",
            json={"code": "x = 1"},
            headers=auth_headers,
        )
    assert response.status_code == 200
    call_kwargs = mock_client.stream.call_args
    assert "The code is written in" not in call_kwargs.kwargs["json"]["prompt"]


def test_review_unknown_mode_falls_back_to_full(client, auth_headers, mock_ollama_stream):
    mock_cm, mock_client = mock_ollama_stream()
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/review",
            json={"code": "x = 1", "mode": "unknownmode"},
            headers=auth_headers,
        )
    assert response.status_code == 200
    call_kwargs = mock_client.stream.call_args
    assert "bugs and logic errors" in call_kwargs.kwargs["json"]["prompt"]


def test_review_missing_code_returns_422(client, auth_headers):
    response = client.post("/review", json={"mode": "full"}, headers=auth_headers)
    assert response.status_code == 422


def test_review_response_content_type_is_text_plain(client, auth_headers, mock_ollama_stream):
    mock_cm, _ = mock_ollama_stream()
    with patch("application.app.httpx.AsyncClient", return_value=mock_cm):
        response = client.post(
            "/review",
            json={"code": "x = 1"},
            headers=auth_headers,
        )
    assert "text/plain" in response.headers["content-type"]
