from concurrent.futures import ThreadPoolExecutor
from app.refresh_tokens import hash_token, generate_token, store_refresh_token, claim_token

def test_deterministic_hash():
    assert hash_token("123") == hash_token("123")

def test_known_hash():
    assert hash_token("123") == "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"

def test_unique_tokens():
    assert generate_token() != generate_token()

def test_claim_token_only_succeeds_once():
    raw_token, _ = store_refresh_token(1)

    assert claim_token(raw_token) is True
    assert claim_token(raw_token) is False

def test_claim_unknown_token():
    assert claim_token("fake-token") is False

def test_claim_token_concurrent_single_winner():
    raw_token, _ = store_refresh_token(1)

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(lambda _: claim_token(raw_token), range(10)))

    assert results.count(True) == 1
    assert results.count(False) == 9