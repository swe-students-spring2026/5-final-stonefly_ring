import importlib
from unittest.mock import MagicMock, patch

import requests as req_lib


def load_frontend_module(monkeypatch):
    monkeypatch.setenv("API_URL", "http://localhost:5001")
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-secret")
    module = importlib.import_module("frontend.app")
    return importlib.reload(module)


def create_test_client(monkeypatch):
    frontend_module = load_frontend_module(monkeypatch)
    frontend_module.app.config["TESTING"] = True
    return frontend_module.app.test_client()


def set_session(client, username="alice"):
    with client.session_transaction() as sess:
        sess["user"] = {"id": "1", "username": username}


def mock_response(status_code=200, ok=True, json_data=None):
    m = MagicMock()
    m.status_code = status_code
    m.ok = ok
    m.json.return_value = json_data or {}
    return m


# --- redirects when not logged in ---

def test_dashboard_redirects_when_not_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_friends_redirects_when_not_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    response = client.get("/friends")
    assert response.status_code == 302


def test_add_redirects_when_not_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    response = client.get("/add")
    assert response.status_code == 302


def test_profile_redirects_when_not_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    response = client.get("/profile")
    assert response.status_code == 302


# --- login ---

def test_login_get_returns_200(monkeypatch):
    client = create_test_client(monkeypatch)
    response = client.get("/login")
    assert response.status_code == 200


def test_login_redirects_to_dashboard_when_already_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    response = client.get("/login")
    assert response.status_code == 302


def test_login_redirects_to_dashboard_on_success(monkeypatch):
    client = create_test_client(monkeypatch)
    mock_resp = mock_response(200, True, {"id": "1", "username": "alice"})

    with patch("frontend.app.requests.post", return_value=mock_resp):
        response = client.post("/login", data={"username": "alice", "password": "secret"})

    assert response.status_code == 302
    assert "/" in response.headers["Location"]


def test_login_stays_on_login_on_failure(monkeypatch):
    client = create_test_client(monkeypatch)
    mock_resp = mock_response(401, False, {"error": "invalid credentials"})

    with patch("frontend.app.requests.post", return_value=mock_resp):
        response = client.post("/login", data={"username": "alice", "password": "wrong"})

    assert response.status_code == 302
    assert "login" in response.headers["Location"]


def test_login_connection_error(monkeypatch):
    client = create_test_client(monkeypatch)

    with patch("frontend.app.requests.post", side_effect=req_lib.exceptions.RequestException):
        response = client.post("/login", data={"username": "alice", "password": "secret"})

    assert response.status_code == 302
    assert "login" in response.headers["Location"]


# --- register ---

def test_register_get_returns_200(monkeypatch):
    client = create_test_client(monkeypatch)
    response = client.get("/register")
    assert response.status_code == 200


def test_register_redirects_when_already_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    response = client.get("/register")
    assert response.status_code == 302


def test_register_success(monkeypatch):
    client = create_test_client(monkeypatch)
    mock_resp = mock_response(201, True, {"id": "1", "username": "alice"})

    with patch("frontend.app.requests.post", return_value=mock_resp):
        response = client.post("/register", data={"username": "alice", "password": "secret"})

    assert response.status_code == 302


def test_register_failure(monkeypatch):
    client = create_test_client(monkeypatch)
    mock_resp = mock_response(409, False, {"error": "username already taken"})

    with patch("frontend.app.requests.post", return_value=mock_resp):
        response = client.post("/register", data={"username": "alice", "password": "secret"})

    assert response.status_code == 302
    assert "register" in response.headers["Location"]


def test_register_connection_error(monkeypatch):
    client = create_test_client(monkeypatch)

    with patch("frontend.app.requests.post", side_effect=req_lib.exceptions.RequestException):
        response = client.post("/register", data={"username": "alice", "password": "secret"})

    assert response.status_code == 302


# --- logout ---

def test_logout_redirects_to_login(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    response = client.get("/logout")
    assert response.status_code == 302
    assert "login" in response.headers["Location"]


# --- logged-in routes ---

def test_dashboard_when_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    mock_friendships = mock_response(200, True, {"friendships": []})
    mock_expenses = mock_response(200, True, {"expenses": []})

    with patch("frontend.app.requests.get", side_effect=[mock_friendships, mock_expenses]):
        response = client.get("/")

    assert response.status_code == 200


def test_friends_when_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    mock_resp = mock_response(200, True, {"friendships": []})

    with patch("frontend.app.requests.get", return_value=mock_resp):
        response = client.get("/friends")

    assert response.status_code == 200


def test_add_expense_get_when_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    mock_resp = mock_response(200, True, {"friendships": []})

    with patch("frontend.app.requests.get", return_value=mock_resp):
        response = client.get("/add")

    assert response.status_code == 200


def test_add_expense_post_success(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    mock_resp = mock_response(201, True, {"id": "expense-1"})

    with patch("frontend.app.requests.post", return_value=mock_resp):
        response = client.post("/add", data={
            "debtor_username": "bob",
            "description": "dinner",
            "total_amount": "30",
            "amount_owed": "15",
            "category": "food",
        })

    assert response.status_code == 302


def test_add_expense_post_failure(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    mock_post = mock_response(400, False, {"error": "bad data"})
    mock_get = mock_response(200, True, {"friendships": []})

    with patch("frontend.app.requests.post", return_value=mock_post):
        with patch("frontend.app.requests.get", return_value=mock_get):
            response = client.post("/add", data={
                "debtor_username": "bob",
                "description": "dinner",
                "total_amount": "30",
                "amount_owed": "15",
            })

    assert response.status_code == 200


def test_profile_when_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    response = client.get("/profile")
    assert response.status_code == 200
