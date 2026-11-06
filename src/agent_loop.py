"""自研最小 Agent Loop：模型输出 JSON 工具调用或最终文本答案。"""

from __future__ import annotations

import json
import re
from typing import Any

from .llm import get_llm
from .tools import build_tool_registry, clear_traces, run_tool
from .rag import SimpleRAG

SYSTEM_PROMPT = """你是一个会使用工具的助手。
若需要工具，只输出一行 JSON，格式严格为：
{"tool": "工具名", "args": {..}}
可用工具：
- search_docs: args={"query": "问题"}  检索本地文档
- list_docs: args={}  列出 docs 下文档名（检索为空时可先看有哪些文档）
- calculator: args={"expression": "1+2*3"}  四则运算
- get_time: args={}  当前时间

若已足够回答，直接输出最终中文答案（不要包 JSON）。
不要编造文档里没有的内容；检索为空时要明确说明。
"""


def _extract_tool_call(text: str) -> dict[str, Any] | None:
    text = text.strip()
    # 允许模型外包了代码块
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "tool" in data:
            data.setdefault("args", {})
            return data
    except json.JSONDecodeError:
        # 再尝试从文本里抓第一段 {...}
        m = re.search(r"\{.*\}", text, re.S)
        if m:
            try:
                data = json.loads(m.group(0))
                if isinstance(data, dict) and "tool" in data:
                    data.setdefault("args", {})
                    return data
            except json.JSONDecodeError:
                return None
    return None


def run_agent(user_query: str, docs_dir: str = "docs", max_steps: int = 4) -> str:
    clear_traces()
    llm = get_llm()
    rag = SimpleRAG(docs_dir)
    tools = build_tool_registry(rag)

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    for step in range(max_steps):
        raw = llm.chat(messages)
        messages.append({"role": "assistant", "content": raw})

        call = _extract_tool_call(raw)
        if not call:
            return raw  # 最终答案

        name = call["tool"]
        args = call.get("args") or {}
        result = run_tool(tools, name, args)
        messages.append(
            {
                "role": "tool",
                "content": f"tool={name} args={args}\nresult:\n{result}",
            }
        )
        # 再催一枪：基于工具结果作答或继续调工具
        messages.append(
            {
                "role": "user",
                "content": "这是工具返回结果。若还需工具请再输出 JSON；否则给出最终答案。",
            }
        )

    return "达到最大步数仍未给出最终答案。请缩小问题或检查工具。"
