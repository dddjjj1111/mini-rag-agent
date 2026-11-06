# 失败案例笔记（Day 3）

## 1. cd 带注释导致路径错误
- **现象**：`cd ~/Downloads/mini-rag-agent   # 解压后的实际路径` 报 `cd: too many arguments`；后面 `pip`/`cp`/`python -m src.main` 都失败。
- **原因**：zsh 里把 `#` 后面的中文当成了额外参数；实际仍停在家目录 `~`，venv 建到了 `~/.venv`。
- **修法**：`cd` 单独一行、不要尾随注释；先 `pwd`/`ls` 确认进了项目目录再装依赖。

## 2. 未开 mock 调真实 API 得到 401
- **现象**：`python -m src.main "..."` 报 `401 Authorization Required`（DeepSeek）。
- **原因**：`.env` 里没有有效密钥，且 `USE_MOCK_LLM` 未开启，代码走了真实 HTTP。
- **修法**：学习阶段用 `USE_MOCK_LLM=1 python -m src.main "..."`，或在 `.env` 写入 `USE_MOCK_LLM=1`。

## 3. 中文整句当分词导致检索空结果
- **现象**：文档 `工具失败.md` 明明存在，`search_docs` 仍返回「未检索到相关文档」。
- **原因**：旧 `_tokenize` 把连续中文当成一个整词，查询「工具失败怎么办」与正文「工具失败时要…」无法交集。
- **修法**：中文再切 bigram（两字一组）后再算重叠；改完后能命中 `工具失败.md`，`pytest` 仍 6 passed。
