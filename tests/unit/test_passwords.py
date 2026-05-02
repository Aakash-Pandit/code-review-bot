from auth.passwords import hash_password, verify_password


def test_hash_password_returns_string():
    result = hash_password("mysecret")
    assert isinstance(result, str)


def test_hash_password_is_not_plaintext():
    result = hash_password("mysecret")
    assert result != "mysecret"


def test_hash_password_produces_different_hashes_each_call():
    h1 = hash_password("samepassword")
    h2 = hash_password("samepassword")
    assert h1 != h2


def test_verify_password_correct_returns_true():
    hashed = hash_password("correcthorse")
    assert verify_password("correcthorse", hashed) is True


def test_verify_password_wrong_returns_false():
    hashed = hash_password("correcthorse")
    assert verify_password("wrongpassword", hashed) is False


def test_verify_password_empty_password_returns_false():
    hashed = hash_password("notempty")
    assert verify_password("", hashed) is False
