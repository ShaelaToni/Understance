"""Data models for the subscription service."""


class User:
    def __init__(self, email):
        self.email = email


class Subscription:
    def __init__(self, user, plan):
        self.user = user
        self.plan = plan
        self.active = True
