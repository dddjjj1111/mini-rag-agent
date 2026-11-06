"""命令行入口：python -m src.main \"你的问题\""""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# 保证从项目根目录运行时可导入
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.agent_loop import run_agent  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser(description="mini-rag-agent")
    parser.add_argument("query", nargs="?", default="什么是 RAG？")
    parser.add_argument("--docs", default="docs")
    args = parser.parse_args()
    answer = run_agent(args.query, docs_dir=args.docs)
    print("\n=== 回答 ===")
    print(answer)


if __name__ == "__main__":
    main()
