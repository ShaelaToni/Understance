"""Data models for the subscription service."""


class User:
    def __init__(self, email):
        self.email = email
        self.has_access = True


class Subscription:
    def __init__(self, user, plan):
        self.user = user
        self.plan = plan
        self.active = True
