from dataclasses import dataclass, field

from understance.domain.finding import Finding


@dataclass(frozen=True)
class Module:
    name: str


@dataclass(frozen=True)
class Dependency:
    source: str
    target: str
    line: int | None = field(default=None, compare=False)
    file: str | None = field(default=None, compare=False)


@dataclass(frozen=True)
class DependencyGraph:
    modules: tuple[Module, ...]
    dependencies: tuple[Dependency, ...]

    def __post_init__(self):
        object.__setattr__(self, "modules", tuple(self.modules))
        object.__setattr__(self, "dependencies", tuple(self.dependencies))

    def orphans(self) -> list[Module]:
        imported = {d.target for d in self.dependencies if d.source != d.target}
        return sorted(
            (m for m in self.modules if m.name not in imported),
            key=lambda m: m.name,
        )

    def dependents_of(self, name: str) -> tuple[str, ...]:
        return self._reach(name, {(d.target, d.source) for d in self.dependencies})

    def dependencies_of(self, name: str) -> tuple[str, ...]:
        return self._reach(name, {(d.source, d.target) for d in self.dependencies})

    def _reach(self, name: str, edges: set[tuple[str, str]]) -> tuple[str, ...]:
        known = {m.name for m in self.modules}
        if name not in known:
            return ()
        found: set[str] = set()
        frontier = {name}
        while frontier:
            frontier = {t for s, t in edges if s in frontier and t in known}
            frontier = frontier - found - {name}
            found |= frontier
        return tuple(sorted(found))


@dataclass(frozen=True)
class BlastRadius:
    target: str
    dependents: tuple[str, ...]
    dependencies: tuple[str, ...]
    findings: tuple[Finding, ...]

    def __post_init__(self):
        object.__setattr__(self, "dependents", tuple(self.dependents))
        object.__setattr__(self, "dependencies", tuple(self.dependencies))
        object.__setattr__(self, "findings", tuple(self.findings))
