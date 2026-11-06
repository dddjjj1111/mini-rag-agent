"""Agent 可调用的工具。"""

from __future__ import annotations

import ast
import operator
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


def make_search_docs(rag: SimpleRAG) -> Callable[..., str]:
    def search_docs(query: str) -> str:
        chunks = rag.search(query, top_k=3)
        return rag.format_context(chunks)

    return search_docs


def build_tool_registry(rag: SimpleRAG) -> dict[str, Callable[..., str]]:
    return {
        "search_docs": make_search_docs(rag),
        "calculator": calculator,
        "get_time": get_time,
    }


def run_tool(registry: dict[str, Callable[..., str]], name: str, args: dict[str, Any]) -> str:
    if name not in registry:
        return f"未知工具: {name}。可用: {', '.join(registry)}"
    fn = registry[name]
    try:
        return fn(**args)
    except TypeError as e:
        return f"工具参数错误 ({name}): {e}"
    except Exception as e:  # noqa: BLE001
        return f"工具执行失败 ({name}): {e}"
