# RAG 简介

RAG（Retrieval-Augmented Generation）先检索相关文档片段，再让大模型基于片段回答，用来降低幻觉。

本项目的简化流程：切分文档 → 关键词打分检索 Top-K → 把片段塞进提示词。
