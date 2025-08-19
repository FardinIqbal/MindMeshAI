from typing import List, Optional
from pydantic import BaseModel, Field


class Citation(BaseModel):
    url: str
    title: Optional[str] = None
    tier: Optional[str] = None
    confidence: Optional[float] = None


class Rebuttal(BaseModel):
    summary: str
    explanation: str
    citations: List[Citation]


class RebuttalRequest(BaseModel):
    claim: str
    lens: Optional[List[str]] = None


class RebuttalResponse(BaseModel):
    rebuttals: List[Rebuttal]


class NodeSchema(BaseModel):
    id: str
    text: str
    type: str
    strength: int
    fallacies: List[str] = Field(default_factory=list)
    children: List["NodeSchema"] = Field(default_factory=list)


NodeSchema.update_forward_refs()


class TreeRequest(BaseModel):
    topic: str
    depth: Optional[int] = 1
    lens: Optional[List[str]] = None


class AuditIssue(BaseModel):
    node_id: str
    fallacy_type: str
    severity: int
    suggestion: str
    better_sources: List[str]


class AuditRequest(BaseModel):
    tree_id: str


class AuditResponse(BaseModel):
    issues: List[AuditIssue]


class LensRequest(BaseModel):
    claim: str
    lens: List[str]


class LensPerspective(BaseModel):
    lens: str
    counters: List[str]


class LensResponse(BaseModel):
    perspectives: List[LensPerspective]


class ResearchRequest(BaseModel):
    query: str


class ResearchResponse(BaseModel):
    citations: List[Citation]
