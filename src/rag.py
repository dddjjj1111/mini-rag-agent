"""极简关键词 RAG：不依赖向量库，大二也能看懂、改得动。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    source: str
    text: str


def _tokenize(text: str) -> set[str]:
    # 中英都粗暴按非字母数字中文切；中文再切 bigram，避免整句对不上
    parts = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z0-9_]+", text.lower())
    tokens: set[str] = set()
    for part in parts:
        tokens.add(part)
        if re.fullmatch(r"[\u4e00-\u9fff]+", part) and len(part) >= 2:
            for i in range(len(part) - 1):
                tokens.add(part[i : i + 2])
    return tokens


class SimpleRAG:
    def __init__(self, docs_dir: str | Path) -> None:
        self.docs_dir = Path(docs_dir)
        self.chunks: list[Chunk] = []
        self._load()

    def _load(self) -> None:
        self.chunks.clear()
        if not self.docs_dir.exists():
            return
        for path in sorted(self.docs_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            # 按空行粗切
            for block in re.split(r"\n\s*\n", text):
                block = block.strip()
                if len(block) >= 20:
                    self.chunks.append(Chunk(source=path.name, text=block))

    def search(self, query: str, top_k: int = 3, min_score: float = 0.15) -> list[Chunk]:
        if not self.chunks:
            return []
        q = _tokenize(query)
        if not q:
            return []
        scored: list[tuple[float, Chunk]] = []
        for ch in self.chunks:
            t = _tokenize(ch.text)
            overlap = len(q & t)
            if overlap:
                score = overlap / len(q)
                if score >= min_score:
                    scored.append((score, ch))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored[:top_k]]

    def format_context(self, chunks: list[Chunk]) -> str:
        if not chunks:
            return "（未检索到相关文档）"
        lines = []
        for i, ch in enumerate(chunks, 1):
            lines.append(f"[{i}] 来源: {ch.source}\n{ch.text}")
        return "\n\n".join(lines)
