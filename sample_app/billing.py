"""Billing, driven by subscription state."""

from sample_app.models import Subscription
from sample_app.subscriptions import cancel_subscription


def charge(subscription):
    if subscription.active:
        return 1000
    return 0


def new_trial(user):
    return Subscription(user, "trial")


def refund_on_cancel(subscription):
    cancel_subscription(subscription)
    # A refund amount may depend on WHEN cancellation takes effect.
    return 0
