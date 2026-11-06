"""Agent 可调用的工具。"""

from __future__ import annotations

import ast
import operator
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable

from .rag import SimpleRAG

# 安全计算器：只允许数字与四则运算
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


@dataclass
class ToolTrace:
    name: str
    args: dict[str, Any]
    ok: bool
    error_kind: str | None
    elapsed_ms: float
    result_preview: str


# 最近一次 Agent 运行里的工具调用痕迹（面试时可讲「可观测性」）
_LAST_TRACES: list[ToolTrace] = []


def get_last_traces() -> list[ToolTrace]:
    return list(_LAST_TRACES)


def clear_traces() -> None:
    _LAST_TRACES.clear()


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    raise ValueError("只允许数字和 + - * /")


def calculator(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval")
        value = _eval_node(tree)
        return f"{expression} = {value}"
    except Exception as e:  # noqa: BLE001 - 工具层要返回可读错误
        return f"计算器错误: {e}"


def get_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _shorten_query(query: str) -> str:
    """空结果时去掉疑问尾巴，保留前半关键词。"""
    q = query.strip()
    for suf in ("怎么办？", "怎么办", "是什么？", "是什么", "如何", "怎么", "？", "?"):
        if q.endswith(suf):
            q = q[: -len(suf)].strip()
            break
    # 中文取前 4 字，英文取前两个词
    import re
    hans = re.findall(r"[\u4e00-\u9fff]", q)
    if len(hans) >= 2:
        return "".join(hans[:4])
    words = re.findall(r"[a-zA-Z0-9_]+", q)
    return " ".join(words[:2]) if words else q


def make_search_docs(rag: SimpleRAG) -> Callable[..., str]:
    def search_docs(query: str) -> str:
        chunks = rag.search(query, top_k=3)
        if chunks:
            return rag.format_context(chunks)
        short = _shorten_query(query)
        if short and short != query:
            chunks = rag.search(short, top_k=3)
            if chunks:
                body = rag.format_context(chunks)
                return f"（原查询无命中，已用缩短查询「{short}」重试）\n{body}"
        return rag.format_context([])

    return search_docs


def make_list_docs(rag: SimpleRAG) -> Callable[..., str]:
    def list_docs() -> str:
        names = sorted(p.name for p in rag.docs_dir.glob("*.md"))
        if not names:
            return "（docs 目录为空）"
        return "文档列表:\n" + "\n".join(f"- {n}" for n in names)

    return list_docs


def build_tool_registry(rag: SimpleRAG) -> dict[str, Callable[..., str]]:
    return {
        "search_docs": make_search_docs(rag),
        "list_docs": make_list_docs(rag),
        "calculator": calculator,
        "get_time": get_time,
    }


def _classify_error(name: str, result: str) -> tuple[bool, str | None]:
    if result.startswith("未知工具"):
        return False, "unknown_tool"
    if result.startswith("工具参数错误"):
        return False, "bad_args"
    if result.startswith("工具执行失败"):
        return False, "exec_error"
    if result.startswith("计算器错误"):
        return False, "bad_args"
    if name == "search_docs" and "未检索到相关文档" in result:
        return True, "empty_result"
    return True, None


def run_tool(registry: dict[str, Callable[..., str]], name: str, args: dict[str, Any]) -> str:
    started = time.perf_counter()
    if name not in registry:
        result = f"未知工具: {name}。可用: {', '.join(registry)}"
    else:
        fn = registry[name]
        try:
            result = fn(**args)
        except TypeError as e:
            result = f"工具参数错误 ({name}): {e}"
        except Exception as e:  # noqa: BLE001
            result = f"工具执行失败 ({name}): {e}"

    elapsed_ms = (time.perf_counter() - started) * 1000
    ok, error_kind = _classify_error(name, result)
    _LAST_TRACES.append(
        ToolTrace(
            name=name,
            args=dict(args or {}),
            ok=ok,
            error_kind=error_kind,
            elapsed_ms=round(elapsed_ms, 3),
            result_preview=result[:200],
        )
    )
    return result


def traces_as_dicts() -> list[dict[str, Any]]:
    return [asdict(t) for t in _LAST_TRACES]
