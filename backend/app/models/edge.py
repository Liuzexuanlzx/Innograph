from enum import Enum

from pydantic import BaseModel, Field


class RelationType(str, Enum):
    """L1: High-level relation type between two papers."""

    IMPROVES_ON = "IMPROVES_ON"
    EXTENDS = "EXTENDS"
    COMBINES_WITH = "COMBINES_WITH"
    APPLIES_TO = "APPLIES_TO"
    SIMPLIFIES = "SIMPLIFIES"
    GENERALIZES = "GENERALIZES"
    PROVIDES_THEORY_FOR = "PROVIDES_THEORY_FOR"
    REPRODUCES = "REPRODUCES"
    CONTRADICTS = "CONTRADICTS"


class InnovationDimension(str, Enum):
    """L2: What dimension of innovation the edge represents."""

    ACCURACY = "ACCURACY"
    EFFICIENCY = "EFFICIENCY"
    SCALABILITY = "SCALABILITY"
    ROBUSTNESS = "ROBUSTNESS"
    GENERALIZATION = "GENERALIZATION"
    INTERPRETABILITY = "INTERPRETABILITY"
    DATA_EFFICIENCY = "DATA_EFFICIENCY"
    SIMPLICITY = "SIMPLICITY"
    NOVELTY = "NOVELTY"
    COVERAGE = "COVERAGE"
    FAIRNESS = "FAIRNESS"
    SAFETY = "SAFETY"
    COST = "COST"
    USABILITY = "USABILITY"


class Operation(str, Enum):
    """L3: Specific technical operation that constitutes the innovation."""

    ADDS_MODULE = "ADDS_MODULE"
    REPLACES_BACKBONE = "REPLACES_BACKBONE"
    CHANGES_LOSS_FUNCTION = "CHANGES_LOSS_FUNCTION"
    MODIFIES_ARCHITECTURE = "MODIFIES_ARCHITECTURE"
    INTRODUCES_PRETRAINING = "INTRODUCES_PRETRAINING"
    ADDS_DATA_AUGMENTATION = "ADDS_DATA_AUGMENTATION"
    CHANGES_OPTIMIZATION = "CHANGES_OPTIMIZATION"
    ADDS_REGULARIZATION = "ADDS_REGULARIZATION"
    INTRODUCES_NEW_TASK = "INTRODUCES_NEW_TASK"
    CHANGES_REPRESENTATION = "CHANGES_REPRESENTATION"
    SCALES_UP = "SCALES_UP"
    ADDS_FEEDBACK_LOOP = "ADDS_FEEDBACK_LOOP"
    INTRODUCES_BENCHMARK = "INTRODUCES_BENCHMARK"
    PROVIDES_PROOF = "PROVIDES_PROOF"
    COMBINES_MODALITIES = "COMBINES_MODALITIES"


class EvidenceSpan(BaseModel):
    """A span of text from a paper that supports an innovation edge."""

    paper_id: str
    text: str
    section: str | None = None
    score: float = 1.0


class Verdict(str, Enum):
    SUPPORTED = "SUPPORTED"
    WEAK = "WEAK"
    UNSUPPORTED = "UNSUPPORTED"


class InnovationEdge(BaseModel):
    """An edge in the innovation genealogy graph."""

    id: str | None = None
    source_paper_id: str
    target_paper_id: str
    relation_type: RelationType
    innovation_dimensions: list[InnovationDimension] = Field(default_factory=list)
    operations: list[Operation] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    verdict: Verdict = Verdict.UNSUPPORTED
    evidence: list[EvidenceSpan] = Field(default_factory=list)
    summary: str = ""
