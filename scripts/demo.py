"""CLI demo: build an innovation graph for a single DOI/query."""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))


async def main():
    from app.agents.workflow import compile_workflow

    query = sys.argv[1] if len(sys.argv) > 1 else "10.48550/arXiv.1706.03762"
    max_papers = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    print(f"Building innovation graph for: {query}")
    print(f"Max papers: {max_papers}")
    print("-" * 60)

    workflow = compile_workflow()

    initial_state = {
        "user_input": query,
        "seed_paper_id": None,
        "retrieval_plan": {"max_papers": max_papers, "depth": 1},
        "raw_papers": [],
        "paper_cards": [],
        "paper_pairs": [],
        "candidate_edges": [],
        "verified_edges": [],
        "rejected_pairs": [],
        "summaries": {},
        "iteration": 0,
        "max_iterations": 2,
        "errors": [],
    }

    final_state = await workflow.ainvoke(initial_state)

    print(f"\nSeed paper: {final_state.get('seed_paper_id')}")
    print(f"Papers retrieved: {len(final_state.get('raw_papers', []))}")
    print(f"Paper cards: {len(final_state.get('paper_cards', []))}")
    print(f"Verified edges: {len(final_state.get('verified_edges', []))}")
    print(f"Errors: {final_state.get('errors', [])}")

    print("\n--- Verified Innovation Edges ---")
    for edge in final_state.get("verified_edges", []):
        print(f"  {edge.source_paper_id} --[{edge.relation_type.value}]--> {edge.target_paper_id}")
        print(f"    Confidence: {edge.confidence:.2f} | Verdict: {edge.verdict.value}")
        print(f"    Dimensions: {[d.value for d in edge.innovation_dimensions]}")
        print(f"    Summary: {edge.summary}")
        print()

    summaries = final_state.get("summaries", {})
    if summaries.get("lineage_summary"):
        print("--- Lineage Summary ---")
        print(summaries["lineage_summary"])


if __name__ == "__main__":
    asyncio.run(main())
