# LLM Agent 学习与资料整理

## 1. 什么是 Agent？

Agent（智能体）在大语言模型（LLM）领域，指的是能够自主感知环境、规划行动、执行任务，并根据反馈不断调整自身行为的智能系统。

### Agent 的核心特征
- **自主性**：能根据目标和环境自主决策、主动行动。
- **感知与交互**：能感知外部环境（如网页、API、文件系统等），并与之交互。
- **规划与执行**：能根据目标制定计划，并一步步执行。
- **反馈与自我调整**：能根据执行结果和外部反馈，动态调整自己的行为。
- **多工具协作**：通常可以调用多种外部工具，实现"工具增强智能"。

> 以上特性主要参考自人工智能领域权威教材 Russell & Norvig《Artificial Intelligence: A Modern Approach》、Wooldridge《An Introduction to MultiAgent Systems》，以及主流 LLM Agent 框架（如 LangChain、OpenAI Assistants API）官方文档的归纳总结。

#### 主要参考文献
1. Russell, S., & Norvig, P. (2021). Artificial Intelligence: A Modern Approach (4th Edition). Pearson.（第2章 Intelligent Agents）
2. Wooldridge, M. (2009). An Introduction to MultiAgent Systems (2nd Edition). Wiley.
3. LangChain 官方文档：https://python.langchain.com/docs/components/agents/
4. OpenAI Assistants API 文档：https://platform.openai.com/docs/assistants/overview

### 典型例子
- AutoGPT、BabyAGI、Copilot/ChatGPT 插件模式等。

---

## 2. 主流 Agent 框架

### 2.1 LangChain
- **简介**：最受欢迎的 LLM 应用开发框架之一，支持 Agent 构建、工具集成、链式推理等。
- **特点**：多 LLM 支持、多 Agent 类型、丰富工具集成。
- **官网**：[https://www.langchain.com/](https://www.langchain.com/)

### 2.2 LlamaIndex
- **简介**：专注于数据接入和知识增强（RAG），也支持 Agent 任务分解和工具调用。
- **特点**：强大数据索引、支持 Agent 任务链。
- **官网**：[https://www.llamaindex.ai/](https://www.llamaindex.ai/)

### 2.3 OpenAI Function Calling / Assistants API
- **简介**：OpenAI 官方推出的 Agent 能力，支持 LLM 自动调用函数（API）、多轮任务管理。
- **特点**：原生支持函数调用，Assistants API 支持多工具、多线程、持久会话。
- **文档**：[OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview)

### 2.4 AutoGen
- **简介**：微软开源的多 Agent 协作框架，支持多智能体协作解决复杂任务。
- **特点**：多 Agent 协作、灵活对话和任务流控制。
- **GitHub**：[https://github.com/microsoft/autogen](https://github.com/microsoft/autogen)

### 2.5 CrewAI
- **简介**：主打"多智能体协作"，每个 Agent 有不同角色和能力，协同完成任务。
- **特点**：任务分工明确，支持多 Agent 协作。
- **GitHub**：[https://github.com/joaomdmoura/crewAI](https://github.com/joaomdmoura/crewAI)

### 2.6 Haystack Agents
- **简介**：专注于 RAG 和多工具集成，支持 Agent 工作流。
- **特点**：强大检索增强生成（RAG）能力，多工具和多 Agent 协作。
- **官网**：[https://haystack.deepset.ai/](https://haystack.deepset.ai/)

### 2.7 AutoGPT / BabyAGI / MetaGPT 等实验性项目
- **简介**：以"自主智能体"为目标的开源项目，能自动分解目标、规划任务、调用工具。
- **GitHub**：
  - [AutoGPT](https://github.com/Significant-Gravitas/Auto-GPT)
  - [BabyAGI](https://github.com/yoheinakajima/babyagi)
  - [MetaGPT](https://github.com/geekan/MetaGPT)

---

## 3. 后续学习内容记录

> 你可以将后续所有 agent 相关的学习笔记、代码片段、心得体会等都补充到本文件中。
