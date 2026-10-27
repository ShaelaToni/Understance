"""Access control: who can sign in, and who can use paid features."""

from sample_app.models import User


def authenticate(email, password):
    # Minimal placeholder; real authentication is out of scope for the fixture.
    return User(email)


def has_access(subscription):
    # Imported inside the function on purpose: subscriptions also imports this
    # module, so a top-level import here would fail at load time (a real cycle).
    from sample_app.subscriptions import is_active

    return is_active(subscription)


def revoke_access(subscription):
    subscription.user.has_access = False
    return subscription.user
