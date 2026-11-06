import os

from src.agent_loop import run_agent


def test_agent_runs_with_mock(tmp_path, monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "1")
    # 复制最少文档目录：直接用项目 docs
    root_docs = os.path.join(os.path.dirname(__file__), "..", "docs")
    out = run_agent("Git 的 commit 是做什么的？", docs_dir=root_docs, max_steps=3)
    assert isinstance(out, str)
    assert len(out) > 0
