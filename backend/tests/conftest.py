import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_openalex_work():
    return {
        "id": "https://openalex.org/W2741809807",
        "doi": "https://doi.org/10.48550/arXiv.1706.03762",
        "title": "Attention Is All You Need",
        "abstract_inverted_index": {
            "The": [0],
            "dominant": [1],
            "sequence": [2],
            "transduction": [3],
            "models": [4],
            "are": [5],
            "based": [6],
            "on": [7],
            "complex": [8],
            "recurrent": [9],
            "or": [10],
            "convolutional": [11],
            "neural": [12],
            "networks.": [13],
        },
        "authorships": [
            {"author": {"display_name": "Ashish Vaswani"}},
            {"author": {"display_name": "Noam Shazeer"}},
        ],
        "publication_year": 2017,
        "primary_location": {
            "source": {"display_name": "NeurIPS"}
        },
        "cited_by_count": 90000,
        "referenced_works": ["https://openalex.org/W1", "https://openalex.org/W2"],
        "concepts": [
            {"display_name": "Attention mechanism"},
            {"display_name": "Transformer"},
        ],
    }


@pytest.fixture
def sample_s2_paper():
    return {
        "paperId": "abc123",
        "externalIds": {"DOI": "10.48550/arXiv.1706.03762"},
        "title": "Attention Is All You Need",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
        "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}],
        "year": 2017,
        "venue": "NeurIPS",
        "citationCount": 90000,
        "referenceCount": 40,
        "fieldsOfStudy": ["Computer Science"],
    }
