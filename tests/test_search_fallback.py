from src.rag import SimpleRAG
from src.tools import build_tool_registry, clear_traces, get_last_traces, run_tool


def test_min_score_filters_weak_hits():
    rag = SimpleRAG("docs")
    # 极低阈值应更容易命中；高阈值应收紧
    loose = rag.search("工具", top_k=5, min_score=0.01)
    tight = rag.search("工具", top_k=5, min_score=0.99)
    assert len(loose) >= len(tight)


def test_search_fallback_shorten():
    clear_traces()
    reg = build_tool_registry(SimpleRAG("docs"))
    # 带尾巴的问句应能通过缩短命中
    out = run_tool(reg, "search_docs", {"query": "工具失败怎么办呀请问一下"})
    assert "工具失败" in out or "缩短查询" in out
    assert get_last_traces()[0].name == "search_docs"
