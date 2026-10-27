"""The service API, wiring the pieces together."""

from sample_app.access import authenticate
from sample_app.billing import refund_on_cancel
from sample_app.notifications import notify_cancellation
from sample_app.subscriptions import create_subscription


def start(email, password, plan):
    user = authenticate(email, password)
    return create_subscription(user, plan)


def end(subscription):
    refund_on_cancel(subscription)
    return notify_cancellation(subscription)
