import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO

@pytest.fixture
def client():
    from main import app
    app.config["TESTING"] = True
    return app.test_client()

def test_create_publication_success(client):
    mock_token = "mocktoken"
    mock_user_id = "user123"
    payload = {
        "Text": "Test publication",
        "Multimedia": {
            "image_base64": "aGVsbG8gd29ybGQ=",  # base64 of "hello world"
            "content_type": "image/png"
        }
    }

    with patch("main.jwt.decode") as mock_jwt_decode, \
         patch("services.functions.conection_mongo") as mock_mongo, \
         patch("services.functions.conection_redis") as mock_redis:

        mock_jwt_decode.return_value = {"user_id": mock_user_id}

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.insert_one.return_value.inserted_id = "pub123"
        mock_mongo.return_value = mock_db

        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        response = client.post(
            "/create-publication",
            headers={"Authorization": f"Bearer {mock_token}"},
            json=payload
        )

        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "Publication created"
        assert data["publication_id"] == "pub123"
