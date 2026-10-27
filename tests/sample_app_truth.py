# Hand-verified expected graph for sample_app (BUILD_ORDER 2.1).
# Modules are the app's .py files; sample_app/tests/ is test evidence, not
# modules (the reader excludes it and says so in its scope line).

EXPECTED_MODULES = (
    "sample_app.access",
    "sample_app.api",
    "sample_app.billing",
    "sample_app.main",
    "sample_app.models",
    "sample_app.notifications",
    "sample_app.subscriptions",
)

# Every import, wherever it appears in the file (top level or inside a
# function). access -> subscriptions is inside has_access().
EXPECTED_DEPENDENCIES = (
    ("sample_app.main", "sample_app.api"),
    ("sample_app.api", "sample_app.access"),
    ("sample_app.api", "sample_app.billing"),
    ("sample_app.api", "sample_app.notifications"),
    ("sample_app.api", "sample_app.subscriptions"),
    ("sample_app.access", "sample_app.models"),
    ("sample_app.access", "sample_app.subscriptions"),
    ("sample_app.billing", "sample_app.models"),
    ("sample_app.billing", "sample_app.subscriptions"),
    ("sample_app.notifications", "sample_app.subscriptions"),
    ("sample_app.subscriptions", "sample_app.access"),
    ("sample_app.subscriptions", "sample_app.models"),
)

EXPECTED_ORPHANS = ("sample_app.main",)

# One import chain: main -> api -> billing -> subscriptions -> models.
EXPECTED_CHAIN = (
    "sample_app.main",
    "sample_app.api",
    "sample_app.billing",
    "sample_app.subscriptions",
    "sample_app.models",
)

# One circular dependency: subscriptions <-> access.
EXPECTED_CYCLE = ("sample_app.access", "sample_app.subscriptions")

# One untested module: no fixture test imports it.
EXPECTED_UNTESTED = ("sample_app.notifications",)
