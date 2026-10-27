from understance.domain.answer import Narration
from understance.domain.finding import Finding
from understance.ports.interfaces import Narrator

TEMPLATE_MODEL = "template (no model)"


class TemplateNarrator(Narrator):
    """Sample mode: state each finding with its file and line; no model call."""

    def narrate(self, findings: tuple[Finding, ...]) -> Narration:
        if not findings:
            text = "No other module imports this one, so no import links lead into it."
            return Narration(text, TEMPLATE_MODEL)
        lines = [f"{len(findings)} import links lead into this module:"]
        lines.extend(f"- {f.summary} ({_location(f)})" for f in findings)
        return Narration("\n".join(lines), TEMPLATE_MODEL)


def _location(finding: Finding) -> str:
    evidence = finding.evidence[0]
    if evidence.line_start is None:
        return evidence.file
    return f"{evidence.file}, line {evidence.line_start}"
