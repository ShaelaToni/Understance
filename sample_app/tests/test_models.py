from sample_app.models import Subscription, User


def test_new_subscription_is_active():
    assert Subscription(User("a@example.com"), "pro").active
