import ast
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src" / "understance"

# Each inner-ring package maps to the understance subpackages it may import.
ALLOWED_INNER = {
    "domain": {"domain"},
    "ports": {"domain", "ports"},
    "usecases": {"domain", "ports", "usecases"},
}


def _is_forbidden(module, ring):
    parts = module.split(".")
    top = parts[0]
    if top == "understance":
        sub = parts[1] if len(parts) > 1 else None
        return sub is not None and sub not in ALLOWED_INNER[ring]
    return top not in sys.stdlib_module_names


def _violations(source, ring):
    bad = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_forbidden(alias.name, ring):
                    bad.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                bad.append("." * node.level + (node.module or ""))
            elif node.module and _is_forbidden(node.module, ring):
                bad.append(node.module)
    return bad


def test_inner_rings_import_only_inward_and_stdlib():
    offences = {}
    for ring in ALLOWED_INNER:
        for path in (SRC / ring).rglob("*.py"):
            bad = _violations(path.read_text(encoding="utf-8"), ring)
            if bad:
                offences[str(path)] = bad
    assert offences == {}, f"forbidden imports in inner rings: {offences}"


def test_checker_flags_a_third_party_import():
    assert _violations("import requests\n", "domain") == ["requests"]


def test_checker_flags_an_outward_import():
    source = "from understance.adapters.zetaris import Thing\n"
    assert _violations(source, "domain") == ["understance.adapters.zetaris"]


def test_checker_flags_a_relative_import():
    assert _violations("from ..adapters import thing\n", "domain") == ["..adapters"]


def test_checker_allows_inner_and_stdlib_imports():
    source = (
        "import ast\n"
        "from dataclasses import dataclass\n"
        "from understance.domain.graph import DependencyGraph\n"
    )
    assert _violations(source, "ports") == []
