from app.infrastructure.security import hash_password, verify_password


def test_hash_and_verify_password_roundtrip() -> None:
    password = "sebastian-murilo-eugenia-farcan-mehdi"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False

