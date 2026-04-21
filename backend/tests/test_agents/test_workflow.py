from app.agents.state import InnoGraphState
from app.agents.workflow import should_retry


class TestWorkflowRouting:
    def test_should_retry_with_rejected_pairs(self):
        state: InnoGraphState = {
            "user_input": "test",
            "seed_paper_id": None,
            "retrieval_plan": {},
            "raw_papers": [],
            "paper_cards": [],
            "paper_pairs": [],
            "candidate_edges": [],
            "verified_edges": [],
            "rejected_pairs": [("a", "b")],
            "summaries": {},
            "iteration": 1,
            "max_iterations": 2,
            "errors": [],
        }
        assert should_retry(state) == "retry"

    def test_should_not_retry_at_max_iterations(self):
        state: InnoGraphState = {
            "user_input": "test",
            "seed_paper_id": None,
            "retrieval_plan": {},
            "raw_papers": [],
            "paper_cards": [],
            "paper_pairs": [],
            "candidate_edges": [],
            "verified_edges": [],
            "rejected_pairs": [("a", "b")],
            "summaries": {},
            "iteration": 2,
            "max_iterations": 2,
            "errors": [],
        }
        assert should_retry(state) == "continue"

    def test_should_continue_no_rejected(self):
        state: InnoGraphState = {
            "user_input": "test",
            "seed_paper_id": None,
            "retrieval_plan": {},
            "raw_papers": [],
            "paper_cards": [],
            "paper_pairs": [],
            "candidate_edges": [],
            "verified_edges": [],
            "rejected_pairs": [],
            "summaries": {},
            "iteration": 1,
            "max_iterations": 2,
            "errors": [],
        }
        assert should_retry(state) == "continue"
