from src.rag import SimpleRAG
from src.tools import build_tool_registry, clear_traces, get_last_traces, run_tool


def test_search_chinese_hit_and_trace():
    clear_traces()
    rag = SimpleRAG("docs")
    reg = build_tool_registry(rag)
    out = run_tool(reg, "search_docs", {"query": "工具失败怎么办？"})
    assert "工具失败" in out
    traces = get_last_traces()
    assert len(traces) == 1
    assert traces[0].name == "search_docs"
    assert traces[0].ok is True
    assert traces[0].error_kind is None


def test_empty_search_marked():
    clear_traces()
    rag = SimpleRAG("docs")
    reg = build_tool_registry(rag)
    out = run_tool(reg, "search_docs", {"query": "完全不存在的火星文档xyz999"})
    assert "未检索到" in out
    t = get_last_traces()[0]
    assert t.error_kind == "empty_result"


def test_unknown_tool_trace():
    clear_traces()
    rag = SimpleRAG("docs")
    reg = build_tool_registry(rag)
    out = run_tool(reg, "no_such_tool", {})
    assert "未知工具" in out
    assert get_last_traces()[0].error_kind == "unknown_tool"


def test_list_docs():
    rag = SimpleRAG("docs")
    reg = build_tool_registry(rag)
    out = run_tool(reg, "list_docs", {})
    assert "文档列表" in out
    assert ".md" in out
