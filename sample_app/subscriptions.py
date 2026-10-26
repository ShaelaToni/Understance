"""Subscription lifecycle, including cancellation."""

from sample_app.models import Subscription


def create_subscription(user, plan):
    return Subscription(user, plan)


def cancel_subscription(subscription):
    # AMBIGUOUS: does cancellation take effect immediately, or at the end of
    # the current billing period? The intended timing is not specified here.
    subscription.active = False
    return subscription
