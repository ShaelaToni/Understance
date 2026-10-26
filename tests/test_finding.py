from dataclasses import FrozenInstanceError

import pytest

from understance.domain.finding import Evidence, Finding, FindingKind, Provenance


def test_evidence_holds_a_file_pointer():
    e = Evidence(file="src/app/billing.py")
    assert e.file == "src/app/billing.py"
    assert e.line_start is None
    assert e.line_end is None
    assert e.content_hash is None


def test_evidence_can_carry_a_line_span_and_hash():
    e = Evidence(
        file="src/app/billing.py", line_start=10, line_end=20, content_hash="abc123"
    )
    assert e.line_start == 10
    assert e.line_end == 20
    assert e.content_hash == "abc123"


def test_evidence_is_immutable():
    e = Evidence(file="src/app/billing.py")
    with pytest.raises(FrozenInstanceError):
        e.file = "other.py"


def test_provenance_records_entity_activity_agent():
    p = Provenance(
        entity="DependencyGraph", activity="read_graph", agent="SourceReader"
    )
    assert p.entity == "DependencyGraph"
    assert p.activity == "read_graph"
    assert p.agent == "SourceReader"


def test_provenance_is_immutable():
    p = Provenance(entity="x", activity="y", agent="z")
    with pytest.raises(FrozenInstanceError):
        p.agent = "other"


def test_finding_carries_its_kind_and_evidence():
    e = Evidence(file="src/app/billing.py", line_start=10, line_end=20)
    f = Finding(
        summary="billing imports auth", kind=FindingKind.OBSERVED, evidence=(e,)
    )
    assert f.kind is FindingKind.OBSERVED
    assert f.evidence == (e,)


def test_finding_distinguishes_observed_from_inferred():
    assert FindingKind.OBSERVED is not FindingKind.INFERRED
    e = Evidence(file="x.py")
    inferred = Finding(
        summary="likely affected", kind=FindingKind.INFERRED, evidence=(e,)
    )
    assert inferred.kind is FindingKind.INFERRED


def test_finding_rejects_empty_evidence():
    with pytest.raises(ValueError):
        Finding(summary="unbacked claim", kind=FindingKind.OBSERVED, evidence=())


def test_finding_normalizes_evidence_to_a_tuple():
    e = Evidence(file="x.py")
    f = Finding(summary="s", kind=FindingKind.OBSERVED, evidence=[e])
    assert isinstance(f.evidence, tuple)


def test_finding_is_immutable():
    e = Evidence(file="x.py")
    f = Finding(summary="s", kind=FindingKind.OBSERVED, evidence=(e,))
    with pytest.raises(FrozenInstanceError):
        f.summary = "other"
