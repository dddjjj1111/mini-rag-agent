# Mini RAG Agent

A small Python demo of **keyword RAG** plus an **agent loop** (decide → call tools → answer).

## Features

- Search Markdown files under `docs/`
- Agent loop with tools (`search_docs`, simple calculator, …)
- Optional mock LLM via `USE_MOCK_LLM=1` (no API key needed)
- Tool traces + `list_docs`; search uses `min_score` and a shorten-and-retry fallback
- pytest coverage for the main paths

## Setup (Mac / Linux)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
```

Set `USE_MOCK_LLM=1` in `.env` for offline runs, or add a real API key.

```bash
USE_MOCK_LLM=1 python -m src.main "什么是 RAG？"
pytest -q
```

## Layout

```
src/     # llm, rag, tools, agent_loop, main
docs/    # knowledge base
tests/   # pytest
notes/   # failure cases and debugging notes
```

## Notes

- Keyword / bigram retrieval, not a vector database
- Keep secrets in `.env` (gitignored); never commit API keys
