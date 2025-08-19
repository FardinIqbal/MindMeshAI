from uuid import uuid4
from typing import Dict, List

from fastapi import FastAPI

from .schemas import (
    AuditIssue,
    AuditRequest,
    AuditResponse,
    Citation,
    LensPerspective,
    LensRequest,
    LensResponse,
    NodeSchema,
    Rebuttal,
    RebuttalRequest,
    RebuttalResponse,
    ResearchRequest,
    ResearchResponse,
    TreeRequest,
)

app = FastAPI(title="Aegis API")


# In-memory store for generated trees
trees: Dict[str, NodeSchema] = {}


def _make_citation(idx: int, topic: str) -> Citation:
    return Citation(
        url=f"https://example.com/{topic.replace(' ', '_')}/{idx}",
        title=f"Source {idx}",
        tier="B",
        confidence=0.9,
    )


@app.post("/api/rebuttal", response_model=RebuttalResponse)
async def generate_rebuttal(payload: RebuttalRequest) -> RebuttalResponse:
    rebuttals: List[Rebuttal] = []
    for i in range(3):
        rebuttals.append(
            Rebuttal(
                summary=f"Counterpoint {i + 1} to '{payload.claim}'",
                explanation=
                    f"This is a generated counterargument number {i + 1} addressing '{payload.claim}'.",
                citations=[_make_citation(i + 1, payload.claim)],
            )
        )
    return RebuttalResponse(rebuttals=rebuttals)


def _generate_counter_nodes(claim: str) -> List[NodeSchema]:
    children: List[NodeSchema] = []
    for i in range(3):
        children.append(
            NodeSchema(
                id=str(uuid4()),
                text=f"Counter {i + 1} to {claim}",
                type="counter",
                strength=50,
                fallacies=[],
                children=[],
            )
        )
    return children


@app.post("/api/tree/generate", response_model=NodeSchema)
async def generate_tree(payload: TreeRequest) -> NodeSchema:
    root_id = str(uuid4())
    root = NodeSchema(
        id=root_id,
        text=payload.topic,
        type="claim",
        strength=60,
        fallacies=[],
        children=_generate_counter_nodes(payload.topic),
    )
    trees[root_id] = root
    return root


def _detect_fallacies(node: NodeSchema, issues: List[AuditIssue]) -> None:
    fallacy_words = {"always": "Overgeneralization", "never": "Overgeneralization"}
    for word, fallacy in fallacy_words.items():
        if word in node.text.lower():
            issues.append(
                AuditIssue(
                    node_id=node.id,
                    fallacy_type=fallacy,
                    severity=1,
                    suggestion="Avoid absolute terms",
                    better_sources=[],
                )
            )
    for child in node.children:
        _detect_fallacies(child, issues)


@app.post("/api/audit", response_model=AuditResponse)
async def audit_tree(payload: AuditRequest) -> AuditResponse:
    tree = trees.get(payload.tree_id)
    if not tree:
        return AuditResponse(issues=[])
    issues: List[AuditIssue] = []
    _detect_fallacies(tree, issues)
    return AuditResponse(issues=issues)


@app.post("/api/lens", response_model=LensResponse)
async def lens_view(payload: LensRequest) -> LensResponse:
    perspectives: List[LensPerspective] = []
    for lens in payload.lens:
        perspectives.append(
            LensPerspective(
                lens=lens,
                counters=[f"From a {lens} perspective, {payload.claim} may be flawed."],
            )
        )
    return LensResponse(perspectives=perspectives)


@app.post("/api/research", response_model=ResearchResponse)
async def research(payload: ResearchRequest) -> ResearchResponse:
    citation = Citation(
        url=f"https://en.wikipedia.org/wiki/{payload.query.replace(' ', '_')}",
        title=payload.query.title(),
        tier="B",
        confidence=0.8,
    )
    return ResearchResponse(citations=[citation])
