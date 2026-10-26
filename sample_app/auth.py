"""Authentication for users."""

from sample_app.models import User


def authenticate(email, password):
    # Minimal placeholder; real auth is out of scope for the fixture.
    return User(email)
