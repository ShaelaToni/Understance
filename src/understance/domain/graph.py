from dataclasses import dataclass


@dataclass(frozen=True)
class Module:
    name: str


@dataclass(frozen=True)
class Dependency:
    source: str
    target: str


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
