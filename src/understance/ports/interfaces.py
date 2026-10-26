from abc import ABC, abstractmethod
from pathlib import Path

from understance.domain.finding import Finding
from understance.domain.graph import DependencyGraph


class SourceReader(ABC):
    """Read the subject repo statically and return its dependency graph (read-only)."""

    @abstractmethod
    def read_graph(self, root: Path) -> DependencyGraph:
        """Return the dependency graph for the repo rooted at `root`."""


class FactStore(ABC):
    """Store and serve the facts derived from the repo; the only source of facts."""

    @abstractmethod
    def store_graph(self, graph: DependencyGraph) -> None:
        """Persist the dependency graph."""

    @abstractmethod
    def load_graph(self) -> DependencyGraph:
        """Return the stored dependency graph."""


class Narrator(ABC):
    """Turn findings into prose; the only port that reaches the model."""

    @abstractmethod
    def narrate(self, findings: tuple[Finding, ...]) -> str:
        """Return a plain-language explanation of the given findings."""


class MemoryStore(ABC):
    """Keep the local per-repo record of findings (decisions added later)."""

    @abstractmethod
    def save_finding(self, finding: Finding) -> None:
        """Save a finding to the local record."""

    @abstractmethod
    def load_findings(self) -> tuple[Finding, ...]:
        """Return the findings in the local record."""
