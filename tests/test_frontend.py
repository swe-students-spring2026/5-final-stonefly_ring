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

def test_logout_redirects_to_login(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    response = client.get("/logout")
    assert response.status_code == 302
    assert "login" in response.headers["Location"]

def test_dashboard_when_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    mock_friendships = mock_response(200, True, {"friendships": []})
    mock_expenses = mock_response(200, True, {"expenses": []})
    mock_payments = mock_response(200, True, {"payments": []})

    with patch("frontend.app.requests.get", side_effect=[mock_friendships, mock_expenses, mock_payments]):
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


def test_dashboard_balance_as_payer(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client, username="alice")
    mock_friendships = mock_response(200, True, {"friendships": [{"friend_username": "bob"}]})
    mock_expenses = mock_response(200, True, {"expenses": [
        {"payer_username": "alice", "debtor_username": "bob", "amount_owed": 10.0}
    ]})
    mock_payments = mock_response(200, True, {"payments": []})
    with patch("frontend.app.requests.get", side_effect=[mock_friendships, mock_expenses, mock_payments]):
        response = client.get("/")

    assert response.status_code == 200


def test_dashboard_balance_as_debtor(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client, username="alice")
    mock_friendships = mock_response(200, True, {"friendships": [{"friend_username": "bob"}]})
    mock_expenses = mock_response(200, True, {"expenses": [
        {"payer_username": "bob", "debtor_username": "alice", "amount_owed": 20.0}
    ]})
    mock_payments = mock_response(200, True, {"payments": []})
    with patch("frontend.app.requests.get", side_effect=[mock_friendships, mock_expenses, mock_payments]):
        response = client.get("/")

    assert response.status_code == 200


def test_add_friend_get_when_logged_in(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    response = client.get("/friends/add")
    assert response.status_code == 200


def test_add_friend_post_success(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    mock_resp = mock_response(201, True, {"message": "friend added"})

    with patch("frontend.app.requests.post", return_value=mock_resp):
        response = client.post("/friends/add", data={"friend_username": "bob"})

    assert response.status_code == 200


def test_add_friend_post_failure(monkeypatch):
    client = create_test_client(monkeypatch)
    set_session(client)
    mock_resp = mock_response(404, False, {"error": "user not found"})

    with patch("frontend.app.requests.post", return_value=mock_resp):
        response = client.post("/friends/add", data={"friend_username": "nobody"})

    assert response.status_code == 200

def test_dashboard_with_payments(monkeypatch):
    """Covers lines 50-56 (the payments loop in the dashboard)"""
    client = create_test_client(monkeypatch)
    set_session(client, username="alice")
    
    mock_friendships = mock_response(200, True, {"friendships": [{"friend_username": "bob"}, {"friend_username": "charlie"}]})
    mock_expenses = mock_response(200, True, {"expenses": []})
    mock_payments = mock_response(200, True, {"payments": [
        {"from_username": "alice", "to_username": "bob", "amount": 10.0},
        {"from_username": "charlie", "to_username": "alice", "amount": 5.0}
    ]})

    with patch("frontend.app.requests.get", side_effect=[mock_friendships, mock_expenses, mock_payments]):
        response = client.get("/")

    assert response.status_code == 200


def test_pay_get_route(monkeypatch):
    """Covers lines 189-213 (GET /pay/<friend_username>)"""
    client = create_test_client(monkeypatch)
    set_session(client, username="alice")
    
    mock_expenses = mock_response(200, True, {"expenses": [
        {"payer_username": "alice", "debtor_username": "bob", "amount_owed": 15.0}
    ]})
    mock_payments = mock_response(200, True, {"payments": [
        {"from_username": "bob", "to_username": "alice", "amount": 5.0}
    ]})
    with patch("frontend.app.requests.get", side_effect=[mock_expenses, mock_payments]):
        response = client.get("/pay/bob")
        
    assert response.status_code == 200


def test_pay_post_success(monkeypatch):
    """Covers lines 218-231 (Successful POST /pay/<friend_username>)"""
    client = create_test_client(monkeypatch)
    set_session(client, username="alice")
    
    mock_post = mock_response(200, True, {"message": "payment successful"})
    
    with patch("frontend.app.requests.post", return_value=mock_post):
        response = client.post("/pay/bob", data={"amount": "10", "note": "dinner"})
        
    assert response.status_code == 302


def test_pay_post_failure_with_json(monkeypatch):
    """Covers lines 232-235 (Failed POST with a JSON error message)"""
    client = create_test_client(monkeypatch)
    set_session(client, username="alice")
    
    mock_post = mock_response(400, False, {"error": "Invalid amount"})
    
    with patch("frontend.app.requests.post", return_value=mock_post):
        response = client.post("/pay/bob", data={"amount": "-50", "note": "bad data"})
        
    assert response.status_code == 200


def test_pay_post_failure_with_exception(monkeypatch):
    """Covers line 240 (Failed POST where response is not valid JSON)"""
    from unittest.mock import MagicMock
    client = create_test_client(monkeypatch)
    set_session(client, username="alice")

    mock_post = MagicMock()
    mock_post.ok = False
    mock_post.status_code = 500
    mock_post.json.side_effect = Exception("Not a valid JSON string")
    
    with patch("frontend.app.requests.post", return_value=mock_post):
        response = client.post("/pay/bob", data={"amount": "10"})
        
    assert response.status_code == 200