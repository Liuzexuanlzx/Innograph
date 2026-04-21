# 项目提案

## 暂定题目

**InnoGraph：面向科研文献的、基于证据的创新演化图谱构建**

## 一句话概括

我们想做的不是普通 citation graph，而是一个能自动回答“后续论文相对前人工作到底改进了什么”的 AI 系统。

## 想解决的问题

现有文献工具，例如 Semantic Scholar、Connected Papers，主要告诉我们：

- 哪些论文相关；
- 谁引用了谁；
- 哪些论文值得继续读。

但它们通常不能回答更关键的问题：

- 论文 B 是在 **改进** 论文 A，还是在 **扩展**、**组合**、**迁移应用**、甚至 **反驳** 它？
- 这个创新主要发生在 **精度、效率、鲁棒性、泛化性** 还是别的维度？
- 有没有具体文本证据支持这种判断？

所以研究者仍然需要手动读很多 abstract，自己总结“idea 是怎么演化的”。我们的目标就是把这一步部分自动化。

## 核心想法

把文献探索问题重新定义为：

**Innovation Lineage Extraction**

输入一篇 seed paper 和一批相关论文，输出一个“创新演化图”：

- 节点是论文；
- 边不是普通引用边，而是“创新关系边”；
- 每条边描述一篇论文是如何相对另一篇论文发生变化的；
- 每条边都带有文本证据和置信度。

换句话说，我们建模的是：

`how paper B changes paper A`

而不只是：

`who cites whom`

## 方法草案

整体 pipeline 可以是：

1. **Seed Paper 解析**
   输入 title / DOI / arXiv ID，定位起始论文。

2. **候选论文检索**
   从 OpenAlex、Semantic Scholar 获取 references、citations、related papers。

3. **论文结构化理解**
   用 LLM 为每篇论文抽取：
   `problem / method / gains / datasets / baselines / limitations`

4. **创新关系抽取**
   对论文对 `(A, B)` 预测创新关系，使用三级 taxonomy：
   - L1: 关系类型，例如 `IMPROVES_ON / EXTENDS / COMBINES_WITH / CONTRADICTS`
   - L2: 创新维度，例如 `ACCURACY / EFFICIENCY / ROBUSTNESS / GENERALIZATION`
   - L3: 技术操作，例如 `ADDS_MODULE / MODIFIES_ARCHITECTURE / CHANGES_LOSS`

5. **证据验证**
   再用 verifier 检查这条边是否有文本证据支持，并给 confidence score，过滤 hallucination。

6. **图谱构建与总结**
   输出 innovation lineage graph，并生成简短 narrative summary。

## 为什么这个题目适合作为课程 project

1. **有明确问题**
   现有文献工具无法解释“方法演化路径”。

2. **有 AI 方法**
   用到 LLM 信息抽取、关系分类、验证、多阶段 agent pipeline。

3. **有应用价值**
   可用于文献综述、快速入门一个方向、发现 research gap。

4. **有 feasibility**
   我们已经有现成 prototype，不是空想题。

5. **符合课程要求**
   这不是已发表工作的复述，而是可以包装成一个新的任务定义 + 方法设计。

## 可能的创新点

我们目前可以主打的创新点有三个：

1. **提出一个新任务**
   从 citation graph 转向 innovation lineage extraction。

2. **提出一个结构化表示**
   用三级 taxonomy 表达论文间“如何变化”。

3. **提出一个更可信的流程**
   抽取后再做 evidence-grounded verification，而不是只让 LLM 自由生成结论。

## 数据与实验计划

### 数据来源

- OpenAlex
- Semantic Scholar
- 我们自己构建一个小规模人工标注集

### 推荐聚焦领域

不要一开始做全学科，建议只选一个方向：

- LLM agents
- RAG
- Diffusion models
- Vision Transformers

我更建议优先选 **LLM agents** 或 **RAG**，因为更容易理解方法演化关系。

### 评估方式

1. **关系抽取准确率**
   用人工标注边做 precision / recall / F1

2. **证据质量**
   看 evidence 是否真的支持预测关系

3. **实用性**
   比较普通 citation list 和 InnoGraph 是否更帮助用户理解某一方向的演化

## Baseline / Ablation 草案

### Baseline

1. 只看 citation graph
2. LLM 自由文本比较两篇论文，不做结构化 taxonomy
3. 去掉 verifier，只做关系抽取

### Ablation

1. 去掉 evidence
2. 去掉 verification
3. 把三级 taxonomy 简化成单层标签

## 当前最大风险

1. 现在很多信息还是基于 abstract，细粒度关系可能不够准
2. “创新关系”本身带有一定主观性，标注会有分歧
3. 如果 scope 太大，容易变成工程展示而不是 research proposal

所以更稳妥的策略是：

- 聚焦一个子领域；
- 做小而清晰的标注集；
- 强调“新任务 + 新表示 + 可验证关系抽取”；
- demo 只作为 feasibility 支撑，不作为核心卖点。

## 组内现在需要拍板的 5 件事

1. **最终聚焦哪个子领域？**
2. **主打 research task 还是 system demo？**
   建议主打 research task。
3. **愿不愿意做一个小规模人工标注集？**
   建议做，不然 evaluation 太虚。
4. **presentation 里要不要放 demo？**
   建议放，但只占一小部分。
5. **最后题目偏研究还是偏产品？**
   建议偏研究。

## 推荐结论

我建议我们把这个 project 定位为：

**一个关于“科研文献创新演化关系抽取”的 AI proposal**

而不是：

**一个文献图谱网站 / 工程系统**

这样更容易满足课程评分里的：

- novelty and impact
- technical soundness and feasibility
- clarity and organization
