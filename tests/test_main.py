import pytest
from fastapi.testclient import TestClient
from bson.objectid import ObjectId

from app.main import app
from app.auth import decode_jwt_token
from app.database import messages_collection

@pytest.fixture(scope="module")
def test_client():
    """Create a TestClient instance for the entire module's tests."""
    with TestClient(app) as client:
        yield client

@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """
    A fixture that runs before each test, ensuring the DB is clean if needed.
    """
    await messages_collection.delete_many({})

def test_login_and_jwt(test_client):
    """
    Testing fake login route to genereate JWT's for subsequent API calls.
    """
    user_id = "testuser123"
    response = test_client.get(f"/login/{user_id}")
    assert response.status_code == 200, "Login route must return 200"

    data = response.json()
    assert "token" in data, "Response must contain 'token' field"

    token = data["token"]
    decoded = decode_jwt_token(token)
    assert decoded["sub"] == user_id, "Token 'sub' should match the requested user_id"

def test_create_message(test_client):
    """
    Test POST /messages to store and encrypt messages for the user.
    """
    user_id = "testuser123"

    token_resp = test_client.get(f"/login/{user_id}")
    token = token_resp.json()["token"]

    create_resp = test_client.post(
        "/messages",
        json={"text": "Hello World!"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert create_resp.status_code == 200, "Message creation should succeed"
    data = create_resp.json()
    assert "inserted_id" in data, "Response must contain inserted_id"

def test_get_messages(test_client):
    """
    Test retrieving all messages with user_id => GET /messages/{user_id}.
    """
    user_id = "testuser123"

    token_resp = test_client.get(f"/login/{user_id}")
    token = token_resp.json()["token"]

    create_resp = test_client.post(
        "/messages",
        json={"text": "Hello World!"},
        headers={"Authorization": f"Bearer {token}"}
    )
    inserted_id = create_resp.json()["inserted_id"]

    get_resp = test_client.get(
        f"/messages/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert get_resp.status_code == 200, "Should be able to retrieve messages"
    
    messages = get_resp.json()
    assert len(messages) == 1, "Should have exactly one message"
    msg = messages[0]

    assert msg["id"] == inserted_id, "Returned message ID should match inserted ID"
    assert msg["user_id"] == user_id, "Returned message's user_id should match the token"
    assert msg["decrypted_text"] == "Hello World!", "Decrypted text should match original text"