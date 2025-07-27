import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import types
from unittest.mock import MagicMock

import pytest

from config.settings import Config
from src.rag.web_interface import create_app


class DummyRAG:
    """Light-weight stub that mimics the public surface of ASURAGSystem
    but never touches OpenAI or vector DB – perfect for fast unit tests.
    """

    def __init__(self):
        self._stats = {
            "chunk_overlap": 200,
            "chunk_size": 1000,
            "embedding_model": "dummy-embedding-model",
            "llm_model": "dummy-llm",
            "vector_store": {"collection_name": "test", "total_documents": 42},
        }

    # ---- API expected by web_interface.py ----
    def get_stats(self):
        return self._stats

    def query(self, question: str, top_k: int = 5):  # noqa: D401
        """Return a deterministic mock answer so tests can assert fields."""
        return {
            "answer": f"Echo: {question}",
            "sources": [
                {
                    "title": "Example",
                    "url": "http://example.com",
                    "score": 0.99,
                    "content_preview": "lorem ipsum",
                    "source": "stub",
                }
            ],
        }


@pytest.fixture(scope="module")
def client():
    """Yield a Flask test-client backed by the dummy RAG system."""
    cfg = Config()
    import src.rag.web_interface as web_interface
    # Monkey-patch to avoid needing an application context for template rendering
    web_interface.render_template_string = lambda s: s
    app = web_interface.create_app(cfg, DummyRAG())
    app.testing = True
    with app.test_client() as c:
        yield c


def test_stats_endpoint(client):
    resp = client.get("/stats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["vector_store"]["total_documents"] == 42
    assert data["chunk_size"] == 1000


def test_query_endpoint(client):
    question = "What is campus life like?"
    resp = client.post("/query", json={"question": question})
    assert resp.status_code == 200
    data = resp.get_json()

    # Basic schema checks
    assert data["answer"].startswith("Echo: ")
    assert isinstance(data["sources"], list) and len(data["sources"]) == 1

    # Ensure no unexpected keys missing
    expected_keys = {"answer", "sources"}
    assert expected_keys.issubset(data.keys())


def test_query_endpoint_empty_question(client):
    """Test query endpoint with empty question."""
    resp = client.post("/query", json={"question": ""})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "question missing"


def test_query_endpoint_missing_question(client):
    """Test query endpoint with missing question field."""
    resp = client.post("/query", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "question missing"


def test_query_endpoint_whitespace_question(client):
    """Test query endpoint with whitespace-only question."""
    resp = client.post("/query", json={"question": "   "})
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "question missing"


def test_query_endpoint_long_question(client):
    """Test query endpoint with a very long question."""
    long_question = "What are the best professors for computer science courses at ASU, specifically looking for those who teach CSE 110, CSE 205, and CSE 310, and what are their teaching styles, office hours, and student reviews?" * 5
    resp = client.post("/query", json={"question": long_question})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["answer"].startswith("Echo: ")
    assert isinstance(data["sources"], list)


def test_query_endpoint_special_characters(client):
    """Test query endpoint with special characters in question."""
    special_question = "What about CSE 110 & CSE 205? Also, what's the deal with @ASU_CS?"
    resp = client.post("/query", json={"question": special_question})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["answer"].startswith("Echo: ")
    assert special_question in data["answer"]


def test_query_endpoint_academic_questions(client):
    """Test query endpoint with academic-related questions."""
    academic_questions = [
        "What are the best professors for CSE 110?",
        "How difficult is CSE 205?",
        "What are the grade distributions for MAT 243?",
        "Which professors have the highest ratings?",
        "What courses should I take for a computer science major?"
    ]
    
    for question in academic_questions:
        resp = client.post("/query", json={"question": question})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["answer"].startswith("Echo: ")
        assert question in data["answer"]


def test_query_endpoint_job_questions(client):
    """Test query endpoint with job-related questions."""
    job_questions = [
        "What are the best campus jobs?",
        "How do I get a job at the library?",
        "What are the highest paying student jobs?",
        "How do I apply for work-study positions?",
        "What are good part-time jobs for students?"
    ]
    
    for question in job_questions:
        resp = client.post("/query", json={"question": question})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["answer"].startswith("Echo: ")
        assert question in data["answer"]


def test_query_endpoint_campus_life_questions(client):
    """Test query endpoint with campus life questions."""
    campus_questions = [
        "What are the best dining halls?",
        "Where can I study on campus?",
        "What clubs should I join?",
        "How do I get involved in Greek life?",
        "What are the best places to hang out?"
    ]
    
    for question in campus_questions:
        resp = client.post("/query", json={"question": question})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["answer"].startswith("Echo: ")
        assert question in data["answer"]


def test_query_endpoint_sources_structure(client):
    """Test that sources have the expected structure."""
    resp = client.post("/query", json={"question": "Test question"})
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) > 0
    
    source = data["sources"][0]
    expected_source_keys = {"title", "url", "score", "content_preview", "source"}
    assert expected_source_keys.issubset(source.keys())
    
    # Check data types
    assert isinstance(source["title"], str)
    assert isinstance(source["url"], str)
    assert isinstance(source["score"], (int, float))
    assert isinstance(source["content_preview"], str)
    assert isinstance(source["source"], str)
    
    # Check score range
    assert 0 <= source["score"] <= 1


def test_query_endpoint_multiple_requests(client):
    """Test multiple rapid requests to ensure stability."""
    questions = [
        "What is ASU?",
        "How do I register for classes?",
        "What are the admission requirements?",
        "Where is the library?",
        "How do I contact my advisor?"
    ]
    
    for question in questions:
        resp = client.post("/query", json={"question": question})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["answer"].startswith("Echo: ")
        assert question in data["answer"]


def test_query_endpoint_invalid_json(client):
    """Test query endpoint with invalid JSON."""
    resp = client.post("/query", data="invalid json", content_type="application/json")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "question missing"


def test_query_endpoint_wrong_content_type(client):
    """Test query endpoint with wrong content type."""
    resp = client.post("/query", data="question=test", content_type="application/x-www-form-urlencoded")
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"] == "question missing" 