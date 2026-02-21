"""Unit tests for app.core.security — all pure/synchronous, no DB needed."""
from datetime import timedelta

import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_password_roundtrip():
    hashed = hash_password("mysecretpassword")
    assert verify_password("mysecretpassword", hashed)


def test_verify_password_wrong_password():
    hashed = hash_password("correct-password")
    assert not verify_password("wrong-password", hashed)


def test_verify_password_empty_string():
    hashed = hash_password("nonempty")
    assert not verify_password("", hashed)


def test_create_access_token_payload():
    token = create_access_token({"sub": "user-abc-123"})
    payload = decode_token(token)
    assert payload["sub"] == "user-abc-123"
    assert payload["type"] == "access"
    assert "exp" in payload


def test_create_refresh_token_type_field():
    token = create_refresh_token({"sub": "user-abc-123"})
    payload = decode_token(token)
    assert payload["sub"] == "user-abc-123"
    assert payload["type"] == "refresh"


def test_access_and_refresh_tokens_differ():
    access = create_access_token({"sub": "u1"})
    refresh = create_refresh_token({"sub": "u1"})
    assert access != refresh


def test_expired_token_raises_jwt_error():
    token = create_access_token({"sub": "u1"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(JWTError):
        decode_token(token)
