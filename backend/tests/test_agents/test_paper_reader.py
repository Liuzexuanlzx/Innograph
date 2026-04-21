from app.agents.paper_reader import infer_short_label_from_title, resolve_short_label


class TestPaperReaderShortLabels:
    def test_prefers_prefix_before_colon(self):
        assert infer_short_label_from_title("ReAct: Synergizing Reasoning and Acting in Language Models") == "ReAct"

    def test_extracts_parenthetical_acronym(self):
        assert infer_short_label_from_title("Chain-of-Thought Prompting (CoT) for Reasoning") == "CoT"

    def test_resolve_uses_llm_value_when_present(self):
        assert resolve_short_label("Attention Is All You Need", "Transformer") == "Transformer"

    def test_resolve_falls_back_to_title_heuristic(self):
        assert resolve_short_label("WebShop: Towards Scalable Real-World Web Interaction", "") == "WebShop"
