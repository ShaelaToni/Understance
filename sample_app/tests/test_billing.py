from sample_app.billing import charge, new_trial, refund_on_cancel
from sample_app.models import User


def test_active_subscription_is_charged():
    assert charge(new_trial(User("a@example.com"))) == 1000


def test_refund_on_cancel_returns_zero():
    assert refund_on_cancel(new_trial(User("a@example.com"))) == 0
