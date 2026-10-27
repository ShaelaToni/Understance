from sample_app.api import start


def test_start_creates_active_subscription():
    assert start("a@example.com", "pw", "pro").active
