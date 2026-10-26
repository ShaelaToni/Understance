"""Entry point for the sample subscription service."""

from sample_app.api import start


def run():
    return start("user@example.com", "secret", "pro")
