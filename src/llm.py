"""LLM 客户端：真实 API 或 Mock（无 key 也能跑通流程）。"""

from __future__ import annotations

import json
import os
import re
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class MockLLM:
    """根据用户话里的关键词假装做工具调用，方便离线调试 Agent Loop。"""

    def chat(self, messages: list[dict[str, str]]) -> str:
        user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        # 已有工具结果时给最终回答
        if any(m["role"] == "tool" for m in messages):
            tool_bits = [m["content"] for m in messages if m["role"] == "tool"]
            return "根据工具结果：" + " | ".join(tool_bits)

        lower = user.lower()
        if any(k in user for k in ("计算", "算一下", "+", "-", "*", "/")) or "calculate" in lower:
            expr = user
            m = re.search(r"([0-9\.\+\-\*/\(\)\s]+)", user)
            if m:
                expr = m.group(1).strip()
            return json.dumps({"tool": "calculator", "args": {"expression": expr}}, ensure_ascii=False)

        if any(k in user for k in ("几点", "时间", "日期")):
            return json.dumps({"tool": "get_time", "args": {}}, ensure_ascii=False)

        # 默认走文档检索
        return json.dumps({"tool": "search_docs", "args": {"query": user}}, ensure_ascii=False)


class OpenAICompatLLM:
    def __init__(self) -> None:
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/")
        self.model = os.getenv("LLM_MODEL", "deepseek-chat")
        if not self.api_key:
            raise ValueError("未设置 LLM_API_KEY。可在 .env 里配置，或设 USE_MOCK_LLM=1")

    def chat(self, messages: list[dict[str, str]]) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def get_llm():
    if os.getenv("USE_MOCK_LLM", "0") == "1":
        return MockLLM()
    try:
        return OpenAICompatLLM()
    except ValueError:
        # 没配 key 时自动降级，保证骨架可跑
        return MockLLM()
