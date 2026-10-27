from abc import ABC, abstractmethod
from pathlib import Path

from understance.domain.answer import Decision, Narration
from understance.domain.finding import Finding
from understance.domain.graph import DependencyGraph, OpenQuestion


class FactsUnavailable(Exception):
    """A FactStore could not reach its facts (for example, a service is down)."""


class DataQualityError(Exception):
    """The facts failed a data quality rule, so no agent may reason over them."""


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
    def narrate(self, findings: tuple[Finding, ...]) -> Narration:
        """Return a plain-language explanation of the findings and the model used."""


class MemoryStore(ABC):
    """Keep the owner's decisions for one repo across runs, so no agent asks twice."""

    @abstractmethod
    def record_decision(self, decision: Decision) -> None:
        """Append the decision; a newer decision replaces the older one in recall."""

    @abstractmethod
    def decision_for(self, question: OpenQuestion) -> Decision | None:
        """Return the current decision for this open question, or None."""
