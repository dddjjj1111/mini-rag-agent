from src.rag import SimpleRAG
from src.tools import build_tool_registry, run_tool


def test_vector_search_finds_rag_doc():
    rag = SimpleRAG("docs")
    chunks = rag.search_vector("什么是 RAG", top_k=3)
    assert chunks
    assert any("rag" in c.source.lower() or "RAG" in c.text for c in chunks)


def test_search_docs_vector_mode():
    reg = build_tool_registry(SimpleRAG("docs"))
    out = run_tool(reg, "search_docs", {"query": "RAG", "mode": "vector"})
    assert "未检索到" not in out
    assert "RAG" in out or "检索" in out
