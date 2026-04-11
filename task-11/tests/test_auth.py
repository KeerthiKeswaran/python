from minitest.core import test, fixture, skip

@fixture(scope="session")
def db_connection():
    return "DB_CONNECTED"

@fixture(scope="function")
def temp_dir():
    return "/tmp/test_dir"

def test_login_valid_credentials(db_connection):
    assert db_connection == "DB_CONNECTED"

def test_login_invalid_password():
    assert 1 + 1 == 2

def test_login_expired_token():
    # Intentionally fail to show diff
    status = 200
    expected = 401
    assert status == expected, f"Expected status={expected}, got status={status}"
