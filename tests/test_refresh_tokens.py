from app.refresh_tokens import hash_token, generate_token

def test_deterministic_hash():
    assert hash_token("123") == hash_token("123")

def test_known_hash():
    assert hash_token("123") == "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"

def test_unique_tokens():
    assert generate_token() != generate_token()
