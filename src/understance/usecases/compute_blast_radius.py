from understance.domain.finding import Evidence, Finding, FindingKind
from understance.domain.graph import BlastRadius, Dependency
from understance.ports.interfaces import FactStore


class ComputeBlastRadius:
    """List what a change to one module could affect, with evidence per edge."""

    def __init__(self, store: FactStore):
        self.store = store

    def run(self, target: str) -> BlastRadius:
        graph = self.store.load_graph()
        if target not in {m.name for m in graph.modules}:
            raise ValueError(f"unknown module: {target}")
        dependents = graph.dependents_of(target)
        sources = set(dependents)
        reached = sources | {target}
        edges = sorted(
            (
                d
                for d in graph.dependencies
                if d.source in sources and d.target in reached and d.file is not None
            ),
            key=lambda d: (d.source, d.target),
        )
        return BlastRadius(
            target=target,
            dependents=dependents,
            dependencies=graph.dependencies_of(target),
            findings=tuple(edge_finding(d) for d in edges),
        )


def edge_finding(edge: Dependency) -> Finding:
    return Finding(
        summary=f"{edge.source} imports {edge.target}",
        kind=FindingKind.OBSERVED,
        evidence=(Evidence(file=edge.file, line_start=edge.line, line_end=edge.line),),
    )
