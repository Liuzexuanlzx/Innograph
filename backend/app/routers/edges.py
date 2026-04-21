from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.edge import InnovationEdge, RelationType, Verdict

router = APIRouter()


class EdgePatch(BaseModel):
    relation_type: RelationType | None = None
    confidence: float | None = None
    verdict: Verdict | None = None


@router.get("/{edge_id}")
async def get_edge(edge_id: str) -> InnovationEdge:
    """Get an innovation edge by ID."""
    from app.services.neo4j_service import Neo4jService

    neo4j = Neo4jService()
    try:
        query = """
        MATCH (src:Paper)-[r:INNOVATION {id: $edge_id}]->(tgt:Paper)
        RETURN src.openalex_id AS source, tgt.openalex_id AS target, r
        """
        async with neo4j._driver.session() as session:
            result = await session.run(query, edge_id=edge_id)
            record = await result.single()
            if not record:
                raise HTTPException(status_code=404, detail="Edge not found")

            import json
            from app.models.edge import (
                EvidenceSpan, InnovationDimension, Operation,
            )
            rel = dict(record["r"])
            evidence = json.loads(rel.get("evidence_json", "[]"))
            return InnovationEdge(
                id=rel.get("id"),
                source_paper_id=record["source"],
                target_paper_id=record["target"],
                relation_type=RelationType(rel["relation_type"]),
                innovation_dimensions=[
                    InnovationDimension(d) for d in rel.get("innovation_dimensions", [])
                ],
                operations=[Operation(o) for o in rel.get("operations", [])],
                confidence=rel.get("confidence", 0),
                verdict=Verdict(rel.get("verdict", "UNSUPPORTED")),
                evidence=[EvidenceSpan(**e) for e in evidence],
                summary=rel.get("summary", ""),
            )
    finally:
        await neo4j.close()


@router.patch("/{edge_id}")
async def patch_edge(edge_id: str, patch: EdgePatch) -> dict:
    """Human correction of an edge."""
    from app.services.neo4j_service import Neo4jService

    neo4j = Neo4jService()
    try:
        set_clauses = []
        params = {"edge_id": edge_id}
        if patch.relation_type is not None:
            set_clauses.append("r.relation_type = $relation_type")
            params["relation_type"] = patch.relation_type.value
        if patch.confidence is not None:
            set_clauses.append("r.confidence = $confidence")
            params["confidence"] = patch.confidence
        if patch.verdict is not None:
            set_clauses.append("r.verdict = $verdict")
            params["verdict"] = patch.verdict.value

        if not set_clauses:
            return {"status": "no changes"}

        query = f"""
        MATCH ()-[r:INNOVATION {{id: $edge_id}}]->()
        SET {', '.join(set_clauses)}
        RETURN r.id AS id
        """
        async with neo4j._driver.session() as session:
            result = await session.run(query, **params)
            record = await result.single()
            if not record:
                raise HTTPException(status_code=404, detail="Edge not found")
        return {"status": "updated", "edge_id": edge_id}
    finally:
        await neo4j.close()
