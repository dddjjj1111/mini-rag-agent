# mini-rag-agent

面向地平线类 **LLM / Agent 工程实习** 的最小可跑骨架：

- 自研 Agent Loop（工具调用循环）
- 本地文档关键词 RAG
- pytest 边界用例
- 失败案例笔记模板

> 大二可维护：不依赖向量数据库；无 API Key 时自动用 MockLLM 跑通流程。

## 快速开始

```bash
cd mini-rag-agent
python3 -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt

# 方式 A：无 key，纯本地 Mock
cp .env.example .env
# 把 USE_MOCK_LLM=1

python -m src.main "什么是 RAG？"
python -m src.main "计算 12*7+3"
pytest -q
```

```bash
# 方式 B：接真实大模型（DeepSeek 示例）
# .env 里：
# USE_MOCK_LLM=0
# LLM_API_KEY=sk-xxx
# LLM_BASE_URL=https://api.deepseek.com
# LLM_MODEL=deepseek-chat
```

## 你接下来要改的地方

1. `docs/` 换成你自己的笔记（至少 5 篇）
2. `src/agent_loop.py` 里增强：空检索短路、超时重试
3. `notes/failure_cases.md` 写满 5 条真实踩坑
4. 推到 GitHub，把链接写进简历

## 简历可写（跑通并补笔记后）

- 独立实现 Python Agent：自研 Agent Loop，支持工具调用与本地文档 RAG
- 使用 Git 管理；pytest 覆盖工具失败与空检索等边界
- 记录 LLM/工具失败案例，并写明复现步骤与能力边界
