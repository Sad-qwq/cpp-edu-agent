# 教师智能出题与 RAG 技术设计文档

## 1. 目标

本文档用于指导 cpp-edu-agent 项目落地“教师智能出题”能力，目标是在现有班级、作业、题目、资料、模型配置基础上，补齐以下核心能力：

1. 教师按知识点、题型、难度比例发起智能出题任务。
2. 系统优先检索教材、班级资料、历史优质题目，基于 RAG 辅助大模型生成题目草案。
3. 对题目草案执行结构化校验、重复度校验、答案一致性校验、编程题沙箱验题。
4. 教师在前端审核、编辑、单题重生成后，再保存到现有作业系统。
5. 记录模型配置、任务状态、题目来源、用量日志，满足后续可追踪、可运营、可扩展要求。

## 2. 当前项目现状

当前仓库已经具备以下可复用能力：

1. 现有模型配置与用量日志接口：backend/app/api/endpoints/model_config.py
2. 现有作业、题目、提交模型：backend/app/models/assignment.py
3. 现有作业与题目 CRUD 接口：backend/app/api/endpoints/assignments.py
4. 现有班级资料上传与查询接口：backend/app/api/endpoints/materials.py
5. 现有代码执行接口：backend/app/api/endpoints/sandbox.py

当前仍缺失以下 AI 关键模块：

1. 统一 LLM Client 与 Provider 抽象。
2. 知识库文档解析、切块、Embedding、索引构建。
3. 检索层与重排层。
4. 智能出题任务模型、任务状态流转、任务结果表。
5. 题目草稿自动校验与编程题自动验题。
6. 教师端智能出题工作台。

## 3. 范围定义

### 3.1 一期要做

1. 教师发起智能出题任务。
2. RAG 接入管理员教材与班级资料。
3. 支持选择题、简答题、编程题三类题目生成。
4. 支持编程题生成代码模板、参考解、测试用例。
5. 支持自动校验和教师审核发布到现有 Assignment/Problem。

### 3.2 一期不做

1. 自动生成整份 PPT 讲义。
2. 多轮对话式备课助手。
3. 完整知识图谱推理引擎。
4. 多模型自动投票生成。
5. 生产级分布式容器调度中心。

## 4. 总体架构

建议采用五层式架构：

1. 数据层
   PostgreSQL 主库保存业务数据、知识文档、知识分块、出题任务、题目草稿、验证结果。
2. 知识层
   负责资料入库、切块、Embedding、索引构建、元数据管理。
3. AI 编排层
   负责模型调用、Prompt 构建、任务流转、重试与用量记录。
4. 校验执行层
   负责结构校验、重复度校验、答案校验、编程题样例执行与测试用例验题。
5. 应用层
   教师端智能出题页面、管理员知识库管理页面、后端 API 与异步任务接口。

## 5. 推荐目录拆分

建议在 backend/app 下新增以下目录：

1. backend/app/ai/
2. backend/app/ai/clients/
3. backend/app/ai/prompts/
4. backend/app/ai/retrieval/
5. backend/app/ai/pipeline/
6. backend/app/ai/validators/
7. backend/app/ai/schemas/
8. backend/app/models/ai_question_generation.py
9. backend/app/api/endpoints/ai_question_generation.py
10. backend/app/api/endpoints/knowledge_base.py

## 5.5 技术选型建议

结合当前仓库已有 FastAPI、PostgreSQL、Redis、Celery 依赖，一期建议如下：

1. 异步任务：复用 Celery + Redis，不新增任务框架。
2. LLM 调用：优先走 OpenAI 兼容协议封装，便于后续切换 OpenAI、DeepSeek、通义千问兼容网关。
3. Embedding：同样走统一 OpenAI 兼容封装，避免前期同时维护多套 SDK。
4. 向量库：优先 PostgreSQL + pgvector。
5. PDF 解析：优先使用 pypdf 或 pymupdf。
6. PPT/PPTX 解析：优先使用 python-pptx。
7. 文本切块：项目内自实现即可，一期不必强依赖 LangChain。
8. 检索重排：一期可先做简单相似度排序，二期再补 reranker。

推荐新增后端依赖：

1. openai
2. pgvector
3. pypdf 或 pymupdf
4. python-pptx
5. tiktoken

若想进一步降低心智负担，也可以二期再评估引入：

1. LangChain
2. LlamaIndex

但一期不建议过早接入重框架，否则容易把实现复杂度花在框架适配上，而不是业务闭环上。

建议模块职责如下：

### 5.1 clients

1. model_provider.py：统一 Provider 接口。
2. openai_client.py：OpenAI/兼容 OpenAI 协议客户端。
3. embedding_client.py：Embedding 调用入口。

### 5.2 retrieval

1. ingest.py：资料解析、切块、入库。
2. chunking.py：按文档类型做切块。
3. search.py：关键词检索与向量检索。
4. rerank.py：召回结果重排。

### 5.3 pipeline

1. create_job.py：创建出题任务。
2. generate_blueprint.py：生成题目蓝图。
3. generate_items.py：逐题生成草稿。
4. validate_items.py：结构与语义校验。
5. verify_coding.py：编程题自动验题。
6. publish.py：保存到 Assignment/Problem。

### 5.4 validators

1. schema_validator.py：Pydantic 校验。
2. duplicate_validator.py：题目查重。
3. answer_validator.py：答案一致性校验。
4. coding_validator.py：测试用例与参考解校验。

## 6. 数据模型设计

## 6.1 KnowledgeDocument

用途：记录入库文档元信息。

建议字段：

1. id
2. source_type
   可选值：admin_material、class_material、history_problem、manual_entry
3. source_id
   对应 materials.id 或其他来源 ID
4. class_id
5. teacher_id
6. title
7. file_path
8. mime_type
9. parse_status
   可选值：pending、processing、completed、failed
10. parse_error
11. metadata_json
12. created_at
13. updated_at

## 6.2 KnowledgeChunk

用途：文档切块与检索单元。

建议字段：

1. id
2. document_id
3. chunk_index
4. content
5. content_type
   可选值：theory、example_code、exercise、faq、definition
6. token_count
7. knowledge_tags
   JSON 数组
8. metadata_json
9. embedding
   一期若使用 pgvector，则为向量字段；若先用外部库，可保存为空
10. created_at

## 6.3 QuestionGenerationJob

用途：记录教师发起的一次出题任务。

建议字段：

1. id
2. teacher_id
3. class_id
4. assignment_id
   可为空，表示先生成草稿，不立刻挂到作业
5. status
   可选值：pending、retrieving、blueprinting、generating、validating、reviewing、published、failed
6. topic
7. knowledge_points
   JSON 数组
8. request_payload
   原始生成参数
9. retrieval_summary
10. blueprint_json
11. error_message
12. started_at
13. finished_at
14. created_at

## 6.4 QuestionDraft

用途：存储某个任务下生成的单题草稿。

建议字段：

1. id
2. job_id
3. draft_index
4. type
5. content
6. options
7. correct_answer
8. code_template
9. test_cases
10. reference_solution
11. explanation
12. target_knowledge_points
13. difficulty
14. estimated_score
15. source_chunk_ids
16. validation_status
   可选值：pending、passed、warning、failed
17. validation_report
18. teacher_action
   可选值：pending、accepted、edited、rejected、regenerated
19. published_problem_id
20. created_at
21. updated_at

## 6.5 QuestionValidationRun

用途：记录单题或单次批量校验结果。

建议字段：

1. id
2. draft_id
3. validation_type
   可选值：schema、semantic、duplicate、coding_execution
4. status
5. report_json
6. created_at

## 7. RAG 设计

## 7.1 知识源优先级

生成时按以下优先级召回：

1. 当前班级资料
2. 当前教师私有历史题目
3. 管理员教材知识库
4. 平台优质公共题库

## 7.2 切块策略

建议规则：

1. 理论文本：500 到 900 字符，重叠 80 到 120。
2. 代码示例：整段保留，不跨函数切割。
3. 题目示例：题干、输入输出、样例作为一个块。
4. FAQ：问答对一组一块。

每个 chunk 统一附带 metadata：

1. source_type
2. class_id
3. teacher_id
4. document_name
5. topic
6. knowledge_tags
7. difficulty_hint

## 7.3 检索策略

建议使用混合检索：

1. 先做元数据过滤。
2. 再做关键词检索。
3. 再做向量检索。
4. 最后做重排。

最终进入 Prompt 的上下文建议控制在 4 到 8 个 chunk。

## 7.4 向量库选型

一期推荐：

1. 首选 PostgreSQL + pgvector。
2. 若为了快速演示，也可先用 Chroma 作为临时方案。

推荐 pgvector 的原因：

1. 与当前 Postgres 架构一致。
2. 权限、备份、部署更统一。
3. 后续方便和业务表联查。

## 8. 智能出题任务流

建议任务流如下：

1. 教师创建任务。
2. 校验教师输入参数。
3. 任务状态改为 retrieving。
4. 检索知识库并写回 retrieval_summary。
5. 调用大模型生成题目蓝图。
6. 校验蓝图是否满足题型比例、难度比例、知识点覆盖。
7. 按蓝图逐题生成结构化草稿。
8. 每道草稿做结构校验与语义校验。
9. 编程题额外生成参考解并执行测试用例。
10. 写入草稿表并生成 validation_report。
11. 任务进入 reviewing。
12. 教师审核后，保存到现有 Assignment/Problem。

## 9. 生成策略

强烈建议采用两阶段生成，不要一次性直接生成整套题。

### 9.1 第一阶段：蓝图生成

输入：

1. 教师请求参数。
2. 检索上下文。
3. 可选的历史题风格样本。

输出：

1. 每道题的类型。
2. 对应知识点。
3. 难度。
4. 预计分值。
5. 考察能力点。

### 9.2 第二阶段：逐题生成

对蓝图中的每一道题单独调用模型生成，输出固定 JSON：

1. type
2. content
3. options
4. correct_answer
5. code_template
6. test_cases
7. explanation
8. target_knowledge_points
9. difficulty
10. source_chunk_ids
11. reference_solution

## 10. Prompt 规范

建议将 Prompt 拆成系统提示词、蓝图提示词、单题生成提示词、验题提示词四类。

## 10.1 系统提示词

职责：约束模型角色。

要求：

1. 你是 C++ 教学命题助手。
2. 题目必须严格基于提供的知识上下文。
3. 若上下文不足，必须降级输出风险提示，不能胡编。
4. 输出必须符合 JSON Schema。
5. 编程题必须提供可执行的样例与测试用例。

## 10.2 蓝图提示词

职责：先规划，不直接写题。

输入：

1. 题量。
2. 题型比例。
3. 难度比例。
4. 指定知识点。
5. 检索上下文摘要。

输出：

1. 题目清单蓝图 JSON。

## 10.3 单题生成提示词

职责：逐题生成结构化结果。

输入：

1. 单题蓝图。
2. 相关 chunk。
3. 输出 Schema。

要求：

1. 不输出多余解释性自然语言。
2. 不得省略字段。
3. 选择题 correct_answer 必须命中 options。
4. 编程题 test_cases 至少包含样例和边界用例。

## 10.4 验题提示词

职责：让模型检查题面是否自洽。

输出：

1. 风险等级。
2. 问题列表。
3. 修复建议。

## 11. 自动校验设计

## 11.1 结构校验

使用 Pydantic 对草稿做强校验：

1. 题型合法。
2. 必填字段不为空。
3. 选择题至少两个选项。
4. 编程题必须有测试用例。

## 11.2 语义校验

规则如下：

1. 选择题答案必须存在于选项中。
2. 选择题选项不得高度重复。
3. 简答题评分说明不得与题面冲突。
4. 编程题输入输出描述、样例、测试用例需要一致。

## 11.3 重复度校验

建议同时做两类查重：

1. 与历史题目做向量相似度查重。
2. 与本次生成批次内部做文本相似度查重。

当相似度超过阈值时，不直接丢弃，而是打 warning。

## 11.4 编程题执行校验

流程：

1. 用 reference_solution 编译执行。
2. 逐个跑样例与隐藏测试用例。
3. 若编译失败或运行失败，则标记 failed。
4. 若样例不通过，自动进入一次修复循环。

开发阶段可以暂时复用现有 sandbox 接口，后续必须切换到 Docker 隔离执行。

## 12. API 设计

建议新增以下接口：

### 12.1 创建出题任务

POST /api/v1/ai/question-generation/jobs

请求体建议字段：

1. class_id
2. assignment_id
3. topic
4. knowledge_points
5. total_count
6. question_type_distribution
7. difficulty_distribution
8. use_class_materials
9. use_admin_knowledge_base
10. use_history_questions
11. extra_constraints

返回：

1. job_id
2. status

### 12.2 查询任务详情

GET /api/v1/ai/question-generation/jobs/{job_id}

返回：

1. job 基本信息
2. 当前状态
3. 检索摘要
4. 草稿列表
5. 校验结果

### 12.3 单题重生成

POST /api/v1/ai/question-generation/jobs/{job_id}/drafts/{draft_id}/regenerate

用途：仅重生成一题，避免整套重跑。

### 12.4 发布到作业

POST /api/v1/ai/question-generation/jobs/{job_id}/publish

请求体：

1. assignment_id
2. accepted_draft_ids

用途：将审核通过的草稿写入现有 Problem 表。

### 12.5 知识库入库

POST /api/v1/ai/knowledge/materials/{material_id}/ingest

用途：将现有资料内容解析并切块入库。

### 12.6 检索调试

GET /api/v1/ai/knowledge/search

用途：开发期间调试 RAG 召回质量。

## 13. 与现有作业系统的衔接

发布阶段不要新建另一套题目模型，直接复用现有 Problem：

1. choice 对应现有 options + correct_answer。
2. short_answer 对应 content + correct_answer。
3. coding 对应 content + code_template + test_cases。

发布逻辑建议：

1. 将已接受草稿转换为 ProblemCreate 结构。
2. 调用现有 assignments 接口或同层 service 保存。
3. 保留 draft_id 到 published_problem_id 的映射，便于追溯。

## 14. 前端设计

建议新增教师端页面：

1. frontend/src/views/ai/QuestionGenerationView.vue
2. frontend/src/services/ai-question-generation.ts

页面分为四块：

1. 生成参数表单。
2. 任务进度与日志面板。
3. 草稿预览与校验结果。
4. 单题编辑、重生成、发布区域。

教师侧交互建议：

1. 先选班级和作业。
2. 填主题、知识点、题型比例、难度比例。
3. 点击生成草稿。
4. 前端轮询任务状态。
5. 草稿出来后，逐题查看“题目内容、答案、测试用例、来源片段、验证状态”。
6. 支持编辑后发布。

## 15. 权限控制

1. 只有 teacher/admin 可以发起出题任务。
2. teacher 只能对自己管理的班级发起任务。
3. admin 可以管理全局教材知识库。
4. class_material 类型知识仅允许该班教师或管理员检索。

## 16. 用量与成本控制

出题任务天然是高消耗接口，必须做以下保护：

1. 读取现有 ModelConfig。
2. 记录每次任务 token 消耗。
3. 对单教师、单班级增加频率限制。
4. 题量和上下文长度设置上限。
5. 当日额度接近上限时给出提示。

建议直接复用现有 model_config 配置和日志表，不单独新造配额体系。

## 17. 实现顺序建议

### 阶段一：AI 基础设施

1. 建立统一 LLM Client。
2. 增加 AI 相关数据表。
3. 打通任务状态表与日志记录。

### 阶段二：知识库最小版

1. 先支持 materials 入库。
2. 完成文本解析、切块、Embedding、检索。
3. 增加检索调试接口。

### 阶段三：智能出题后端

1. 创建任务接口。
2. 蓝图生成。
3. 单题生成。
4. 自动校验。
5. 发布到作业。

### 阶段四：教师端页面

1. 生成参数表单。
2. 草稿预览。
3. 单题编辑与重生成。
4. 发布到作业。

### 阶段五：增强能力

1. 引入历史题查重。
2. 支持知识点图谱标签。
3. 支持多模型切换与对比。
4. 将编程题验题从本机执行迁移到 Docker。

## 18. 一期最小可交付版本

为了尽快形成可演示结果，一期建议控制为：

1. 支持教材与班级资料入库。
2. 支持 choice 和 coding 两类题目生成。
3. 支持参考解 + 测试用例自动验题。
4. 支持教师审核后发布到现有作业。

这版已经足够支撑“教师智能出题”答辩演示，并且和当前仓库的作业系统可直接打通。

## 19. 后续可扩展方向

1. 根据班级学情和错题数据做自适应出题。
2. 根据学生画像做分层作业生成。
3. 将 RAG 知识库进一步用于 AI 伴学答疑。
4. 将知识点标签反向写入学情雷达图与学习路径推荐模块。

## 20. 结论

本项目的教师智能出题不应实现为一个简单的“调用大模型生成文本”按钮，而应实现为：

1. 有来源的 RAG 检索。
2. 有约束的结构化生成。
3. 有验证的自动验题。
4. 有教师审核的发布闭环。

这样设计才能真正贴合教学业务，也能最大限度复用当前项目已有的班级、资料、作业、题目和模型配置能力。