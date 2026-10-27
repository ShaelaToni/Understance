from sample_app.main import run


def test_run_starts_pro_subscription():
    assert run().plan == "pro"
