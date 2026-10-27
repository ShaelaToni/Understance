from understance.adapters.template_narrator import TemplateNarrator
from understance.domain.answer import Narration
from understance.domain.finding import Evidence, Finding, FindingKind
from understance.ports.interfaces import Narrator


def _finding(summary, file, line):
    return Finding(summary, FindingKind.OBSERVED, [Evidence(file, line, line)])


def test_template_narrator_implements_the_narrator_port():
    assert isinstance(TemplateNarrator(), Narrator)


def test_each_finding_is_stated_with_its_file_and_line_and_no_model_is_claimed():
    narration = TemplateNarrator().narrate(
        (
            _finding("app.a imports app.b", "app/a.py", 3),
            _finding("app.c imports app.b", "app/c.py", 14),
        )
    )
    assert narration == Narration(
        text=(
            "2 import links lead into this module:\n"
            "- app.a imports app.b (app/a.py, line 3)\n"
            "- app.c imports app.b (app/c.py, line 14)"
        ),
        model="template (no model)",
    )


def test_no_findings_is_said_plainly():
    narration = TemplateNarrator().narrate(())
    assert narration.text == (
        "No other module imports this one, so no import links lead into it."
    )
