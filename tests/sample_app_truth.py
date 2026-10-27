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

# Line of the first import statement behind each edge (hand-read from the files).
EXPECTED_IMPORT_LINES = {
    ("sample_app.main", "sample_app.api"): 3,
    ("sample_app.api", "sample_app.access"): 3,
    ("sample_app.api", "sample_app.billing"): 4,
    ("sample_app.api", "sample_app.notifications"): 5,
    ("sample_app.api", "sample_app.subscriptions"): 6,
    ("sample_app.access", "sample_app.models"): 3,
    ("sample_app.access", "sample_app.subscriptions"): 14,
    ("sample_app.billing", "sample_app.models"): 3,
    ("sample_app.billing", "sample_app.subscriptions"): 4,
    ("sample_app.notifications", "sample_app.subscriptions"): 3,
    ("sample_app.subscriptions", "sample_app.access"): 3,
    ("sample_app.subscriptions", "sample_app.models"): 4,
}

# Hand-traced blast radius (BUILD_ORDER 2.4): who depends on the target, directly
# or through others, and what the target depends on.
EXPECTED_BLAST_RADIUS = {
    "sample_app.subscriptions": {
        "dependents": (
            "sample_app.access",
            "sample_app.api",
            "sample_app.billing",
            "sample_app.main",
            "sample_app.notifications",
        ),
        "dependencies": ("sample_app.access", "sample_app.models"),
    },
    "sample_app.notifications": {
        "dependents": ("sample_app.api", "sample_app.main"),
        "dependencies": (
            "sample_app.access",
            "sample_app.models",
            "sample_app.subscriptions",
        ),
    },
}

# The one decision the code marks as unsettled (an AMBIGUOUS: comment), the demo's
# stop-and-ask: (file, line, enclosing function).
EXPECTED_OPEN_QUESTIONS = {
    "sample_app.subscriptions": (
        ("sample_app/subscriptions.py", 16, "cancel_subscription"),
    ),
}
