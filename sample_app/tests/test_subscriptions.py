from sample_app.models import User
from sample_app.subscriptions import cancel_subscription, create_subscription


def test_cancel_deactivates_and_revokes_access():
    sub = cancel_subscription(create_subscription(User("a@example.com"), "pro"))
    assert sub.active is False
    assert sub.user.has_access is False
