from pathlib import Path

from src.rag import SimpleRAG


def test_search_finds_git_doc():
    root = Path(__file__).resolve().parents[1]
    rag = SimpleRAG(root / "docs")
    hits = rag.search("Git 提交 分支", top_k=3)
    assert hits
    assert any("git" in h.source.lower() or "Git" in h.text for h in hits)


def test_empty_query_returns_empty():
    root = Path(__file__).resolve().parents[1]
    rag = SimpleRAG(root / "docs")
    assert rag.search("   ") == []
