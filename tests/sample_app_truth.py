EXPECTED_MODULES = (
    "sample_app.api",
    "sample_app.auth",
    "sample_app.billing",
    "sample_app.main",
    "sample_app.models",
    "sample_app.notifications",
    "sample_app.subscriptions",
)

EXPECTED_DEPENDENCIES = (
    ("sample_app.main", "sample_app.api"),
    ("sample_app.api", "sample_app.auth"),
    ("sample_app.api", "sample_app.billing"),
    ("sample_app.api", "sample_app.notifications"),
    ("sample_app.api", "sample_app.subscriptions"),
    ("sample_app.billing", "sample_app.models"),
    ("sample_app.billing", "sample_app.subscriptions"),
    ("sample_app.auth", "sample_app.models"),
    ("sample_app.notifications", "sample_app.subscriptions"),
    ("sample_app.subscriptions", "sample_app.models"),
)

EXPECTED_ORPHANS = ("sample_app.main",)
