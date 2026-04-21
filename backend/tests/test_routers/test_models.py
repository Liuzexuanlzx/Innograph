from app.models.paper import Paper, PaperCard
from app.models.edge import (
    InnovationEdge, RelationType, InnovationDimension,
    Operation, EvidenceSpan, Verdict,
)
from app.models.graph import GraphSnapshot
from app.models.task import TaskResult, TaskStatus


class TestPaperModel:
    def test_paper_defaults(self):
        p = Paper(title="Test Paper")
        assert p.citation_count == 0
        assert p.authors == []
        assert p.embedding is None

    def test_paper_card(self):
        c = PaperCard(paper_id="W123", problem="Test problem")
        assert c.short_label == ""
        assert c.method_summary == ""
        assert c.key_modules == []


class TestEdgeModel:
    def test_innovation_edge(self):
        e = InnovationEdge(
            source_paper_id="W1",
            target_paper_id="W2",
            relation_type=RelationType.IMPROVES_ON,
            innovation_dimensions=[InnovationDimension.ACCURACY],
            operations=[Operation.MODIFIES_ARCHITECTURE],
            confidence=0.85,
            verdict=Verdict.SUPPORTED,
            summary="Improves accuracy by modifying architecture",
        )
        assert e.relation_type == RelationType.IMPROVES_ON
        assert e.confidence == 0.85

    def test_evidence_span(self):
        ev = EvidenceSpan(paper_id="W1", text="key finding")
        assert ev.score == 1.0


class TestGraphSnapshot:
    def test_empty_snapshot(self):
        s = GraphSnapshot()
        assert s.papers == []
        assert s.innovation_edges == []


class TestTaskResult:
    def test_pending(self):
        t = TaskResult(task_id="abc")
        assert t.status == TaskStatus.PENDING
