# Mini RAG Agent

极简 **关键词 RAG + Agent Loop** 练习项目（Python）。面向寒假 AI/Agent 实习简历：能本地跑通、有测试、能讲清工具失败边界。

仓库：https://github.com/dddjjj1111/mini-rag-agent

## 能做什么

- 根据问题检索 `docs/` 下的 Markdown
- Agent Loop：决定是否调用工具 → 执行 → 写回上下文 → 最终回答
- 内置工具：`search_docs`、简单计算等
- `USE_MOCK_LLM=1` 时可无 API Key 本地调试

## 快速开始（Mac）

```bash
cd mini-rag-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
cp .env.example .env
# 学习阶段建议在 .env 写：USE_MOCK_LLM=1

USE_MOCK_LLM=1 python -m src.main "什么是 RAG？"
USE_MOCK_LLM=1 python -m src.main "工具失败怎么办？"
pytest -q
```

## 项目结构

```
src/          # llm / rag / tools / agent_loop / main
docs/         # 可检索知识库
tests/        # pytest
notes/        # 失败案例笔记（投简历时很加分）
```

## 简历表述（可直接用）

**Mini RAG Agent｜个人项目｜2026.11**  
技术栈：Python、pytest、Agent Loop、关键词 RAG  

面向 LLM/Agent 工程实践，从零实现「检索增强 + 工具循环」：检索本地 Markdown，经 Agent Loop 调用工具后综合回答。

1. 实现 Agent Loop（思考 → 选工具 → 执行 → 写回），支持步数上限  
2. 自研关键词 RAG（中文 bigram），修复整句中文无法命中的问题  
3. 记录工具失败边界：超时、空结果、非法参数；支持 mock LLM  
4. pytest 覆盖主路径（6 passed）；详见 `notes/failure_cases.md`

投地平线等 JD 可强调：能讲清工具失败与检索空结果时的处理。

## 说明

- 这是学习向骨架，不是生产级向量库 RAG  
- 切勿把真实 API Key 提交进 Git（已忽略 `.env`）
