from sample_app.access import authenticate, has_access, revoke_access
from sample_app.models import Subscription


def test_authenticate_returns_user_with_email():
    assert authenticate("a@example.com", "pw").email == "a@example.com"


def test_active_subscription_has_access():
    sub = Subscription(authenticate("a@example.com", "pw"), "pro")
    assert has_access(sub)


def test_revoke_access_removes_access():
    sub = Subscription(authenticate("a@example.com", "pw"), "pro")
    assert revoke_access(sub).has_access is False
