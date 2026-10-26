"""Notifications sent on subscription events."""

from sample_app.subscriptions import cancel_subscription


def notify_cancellation(subscription):
    cancel_subscription(subscription)
    return f"Subscription for {subscription.user.email} cancelled."
