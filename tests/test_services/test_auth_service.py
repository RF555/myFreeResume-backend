from app.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_access_token,
)


def test_hash_and_verify_password():
    password = "securePassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_and_decode_access_token():
    user_id = "507f1f77bcf86cd799439011"
    token = create_access_token(user_id)
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "access"


def test_create_refresh_token():
    user_id = "507f1f77bcf86cd799439011"
    token = create_refresh_token(user_id)
    assert isinstance(token, str)
    assert len(token) > 0
