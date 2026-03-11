# C++ Education Agent

> 一个面向 C++ 教学场景的智能教学平台，覆盖课程组织、作业训练、讨论答疑、在线实验、AI 出题、AI 助学完整闭环。

## ✨ 项目简介

适合以下场景：

- 高校或培训机构的 C++ 课程教学
- 班级式作业与答疑管理
- 结合知识库与大模型的辅助教学
- 需要在线编译、调试和 AI 学习辅导的实验课程

## 🧭 导航

- ✨ 项目简介
- 🚀 项目亮点
- 🛠️ 技术栈
- 🏗️ 架构概览
- 📚 功能说明
- 🗂️ 目录结构
- 🔌 后端模块
- 🎨 前端体验增强
- ⚡ 快速开始
- 👑 管理员初始化
- 🌐 部署方法
- 🤖 与 AI 相关的说明
- 🧪 常用命令
- 📝 适合继续完善的方向
- ⚠️ 注意事项

## 🚀 项目亮点

| 模块 | 能力 |
| --- | --- |
| 用户与权限 | 支持管理员、教师、学生三种角色 |
| 班级管理 | 创建班级、邀请码加入、成员管理 |
| 作业系统 | 发布作业、题目维护、提交与评分 |
| 讨论答疑 | 提问、回答、点赞、采纳最佳答案 |
| 通知中心 | 集中查看公告、作业与班级动态 |
| 在线实验 | 内置 C++ 沙箱，支持在线编译运行 |
| AI 出题 | 基于资料与知识库生成题目草稿 |
| AI 助学 | 类 ChatGPT/Gemini 对话式辅导 |
| 知识库 | 支持公共知识库与班级知识检索 |

## 🛠️ 技术栈

### 后端

- FastAPI
- SQLModel / SQLAlchemy Async
- PostgreSQL / asyncpg
- Redis
- Pydantic Settings
- OpenAI Compatible API
- pgvector

### 前端

- Vue 3
- TypeScript
- Vite
- Vue Router
- Pinia
- Element Plus
- Tailwind CSS v4
- markdown-it + DOMPurify

## 🏗️ 架构概览

项目采用前后端分离架构：

- 前端负责页面渲染、路由、状态管理和交互体验
- 后端负责业务逻辑、鉴权、数据库访问和 AI 工作流编排
- PostgreSQL 保存业务数据
- Redis 预留给缓存、异步任务或扩展工作流
- AI 模块通过统一的模型提供商接口调用外部大模型服务

后端主入口位于 [backend/main.py](backend/main.py)，统一路由注册位于 [backend/app/api/api.py](backend/app/api/api.py)。

## 📚 功能说明

### 教学管理

- 用户注册、登录、JWT 鉴权
- 管理员审核教师账号
- 班级创建、加入、成员查看
- 平台公告与班级公告管理
- 课程资料上传与组织

### 学习流程

- 教师创建、编辑、删除作业
- 学生查看作业、提交答案、查看分数
- 讨论区提问、回答、点赞、采纳最佳答案
- 通知中心集中查看学习动态
- 在线 C++ 沙箱运行代码

### AI 能力

- AI 智能出题：基于班级资料、公共知识库和模型配置生成题目草稿
- AI 智能助学：围绕班级资料、作业和题目上下文进行会话式辅导
- AI 代码纠错：分析代码、报错信息和期望输出
- 分层提示：按提示级别逐步引导，不直接暴露完整答案
- 练习推荐：根据上下文推荐下一步训练方向

## 🗂️ 目录结构

```text
cpp-edu-agent/
├─ backend/                      后端服务
│  ├─ app/
│  │  ├─ ai/                     AI 客户端、检索、出题、助学流程
│  │  ├─ api/                    FastAPI 路由与依赖
│  │  ├─ core/                   配置与安全逻辑
│  │  ├─ db/                     数据库连接与初始化
│  │  ├─ models/                 SQLModel 模型
│  │  └─ schemas/                请求与响应模型
│  ├─ main.py                    FastAPI 入口
│  ├─ requirements.txt           Python 依赖
│  └─ create_admin_user.py       初始化管理员脚本
├─ frontend/                     Vue 前端
│  ├─ src/
│  │  ├─ layouts/                应用壳层
│  │  ├─ router/                 路由配置
│  │  ├─ services/               API 封装
│  │  ├─ stores/                 Pinia 状态管理
│  │  ├─ utils/                  工具函数，例如主题切换
│  │  └─ views/                  页面视图
│  └─ package.json               前端依赖与脚本
├─ docker-compose.yml            PostgreSQL / Redis 本地依赖
├─ start_all.ps1                 Windows 一键启动脚本
└─ README.md                     项目说明
```

## 🔌 后端模块

当前后端已集成以下路由模块：

- auth：登录注册与鉴权
- users：个人资料、头像、密码、账户信息
- classes：班级与成员管理
- assignments：作业、题目、提交与评分
- discussion：班级讨论区
- notifications：通知中心
- announcements：公告模块
- materials：资料模块
- sandbox：在线 C++ 沙箱
- model：模型配置与模型使用日志
- ai：AI 智能出题
- ai/tutor：AI 智能助学
- ai/knowledge：知识库管理与检索

## 🎨 前端体验增强

前端当前已经包含：

- 更统一的视觉主题
- 白天 / 黑夜主题切换
- 设置页主题持久化
- AI 助学 Markdown 渲染
- 通知、讨论、作业列表分页
- ChatGPT / Gemini 风格 AI 助学工作台

## ⚡ 快速开始

### 1. 环境准备

建议准备以下环境：

- Python 3.11+ 或兼容版本
- Node.js 18+
- npm
- Docker Desktop

### 2. 启动数据库与 Redis

项目根目录执行：

```powershell
docker compose up -d
```

当前 [docker-compose.yml](docker-compose.yml) 会启动：

- PostgreSQL 15
- Redis 7

### 3. 创建并激活 Python 虚拟环境

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 4. 安装后端依赖

```powershell
cd backend
pip install -r requirements.txt
```

### 5. 安装前端依赖

```powershell
cd ../frontend
npm install
```

### 6. 配置环境变量

建议先复制 [.env.example](.env.example) 为 `.env`，再按需修改：

```powershell
Copy-Item .env.example .env
```

`.env` 示例内容如下：

```env
POSTGRES_USER=edu_admin
POSTGRES_PASSWORD=edu_password_123
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=edu_pilot_db

SECRET_KEY=please_change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

AI_PROVIDER=openai-compatible
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=
AI_MODEL_NAME=
AI_EMBEDDING_MODEL=
AI_ENABLE_REMOTE_GENERATION=true
```

说明：

- 不配置 `AI_API_KEY` 时，部分 AI 功能可能回退到本地兜底逻辑
- `SECRET_KEY` 在生产环境必须修改
- 默认数据库配置来源于 [backend/app/core/config.py](backend/app/core/config.py)

### 7. 启动后端

```powershell
cd backend
uvicorn main:app --reload
```

后端默认地址：

- API：`http://127.0.0.1:8000`
- OpenAPI：`http://127.0.0.1:8000/api/v1/openapi.json`
- Swagger：`http://127.0.0.1:8000/docs`

说明：

- 后端启动时会自动执行数据库初始化
- 初始化逻辑位于 [backend/app/db/session.py](backend/app/db/session.py)
- 数据库不可用时，服务会在启动阶段失败

### 8. 启动前端

```powershell
cd frontend
npm run dev
```

前端默认地址：

- `http://127.0.0.1:5173`

### 9. Windows 一键启动

仓库提供了 [start_all.ps1](start_all.ps1)，可在 Windows 上分别拉起前后端开发服务：

```powershell
./start_all.ps1
```

## 👑 管理员初始化

如需创建管理员账号，可执行：

```powershell
cd backend
python create_admin_user.py
```

脚本位于 [backend/create_admin_user.py](backend/create_admin_user.py)。

建议在执行前修改其中的默认管理员邮箱、用户名和密码，避免直接使用开发默认值。

## 🌐 部署方法

下面给出两种比较现实的部署方式。

### 方案一：单机部署，前后端分离

适合云服务器、实验室服务器或内网教学环境。

#### 后端部署

1. 准备服务器环境：Python、Node.js、PostgreSQL、Redis、Nginx
1. 拉取代码并创建虚拟环境
1. 配置项目根目录 `.env`
1. 安装依赖：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

1. 使用 Uvicorn 启动：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

生产环境建议改为使用 `systemd` 或进程守护工具管理后端进程。

#### 前端部署

1. 构建前端：

```bash
cd frontend
npm install
npm run build
```

1. 将 `frontend/dist` 作为静态站点交给 Nginx 托管
1. 通过 Nginx 将 `/api/` 反向代理到 FastAPI 服务

推荐思路：

- `80/443` 端口由 Nginx 对外提供服务
- `/` 指向前端静态文件
- `/api/` 代理到 `127.0.0.1:8000`
- `/static/` 同步代理到后端上传目录映射

### 方案二：Docker 依赖 + 应用手动部署

如果你暂时不想把整套应用 Docker 化，可以采用更稳妥的折中方案：

1. 数据库和 Redis 继续使用 `docker compose up -d`
1. 后端使用 Python 虚拟环境部署
1. 前端使用 `npm run build` 后交给 Nginx

这是当前仓库最容易落地的部署方式，因为仓库已经提供了 [docker-compose.yml](docker-compose.yml)，但尚未提供完整的前后端生产 Dockerfile。

## 📦 生产部署建议

如果要正式上线，建议至少处理以下事项：

1. 修改数据库账号、JWT 密钥、管理员默认密码
1. 限制 CORS，不要继续使用全开放策略
1. 为 Nginx 配置 HTTPS
1. 将 `AI_API_KEY`、数据库密码等敏感信息放入安全的环境变量管理方案中
1. 将 Uvicorn 改为受管进程运行，不要直接手工启动
1. 定期备份 PostgreSQL 数据

## 🤖 与 AI 相关的说明

### AI 智能出题

- 基于班级资料、公共知识库和模型配置生成题目草稿
- 支持将草稿发布到已有作业
- 适合教师快速生成训练题和题目初稿

### AI 智能助学

AI 助学模块当前支持：

- 新建会话、切换历史会话、删除会话
- 概念讲解
- 解题提示
- 代码纠错
- 练习推荐
- Markdown 渲染

相关后端接口位于 [backend/app/api/endpoints/ai_tutor.py](backend/app/api/endpoints/ai_tutor.py)。

## 🧪 常用命令

### 前端开发

```powershell
cd frontend
npm run dev
```

### 前端构建

```powershell
cd frontend
npm run build
```

### 后端开发

```powershell
cd backend
uvicorn main:app --reload
```

### 初始化管理员

```powershell
cd backend
python create_admin_user.py
```

## 📝 适合继续完善的方向

- 补充完整的 Dockerfile 与一键生产部署脚本
- 引入 CI/CD 流程
- 增强 AI 回复的流式输出
- 提升知识库检索质量与引用可视化
- 为更多列表页补充分页、筛选、排序
- 补充自动化测试与接口文档

## ⚠️ 注意事项

- 当前仓库更偏向“可运行的教学平台原型 + 持续增强中的课程系统”
- 如果 PostgreSQL 未启动，后端会在启动阶段失败
- 后端启动时会自动执行 `create_all` 和手工迁移逻辑
- 如果准备公开到 GitHub，当前仓库已经包含 [.env.example](.env.example) 和 [LICENSE](LICENSE)，但仍建议根据你的实际发布策略再次确认内容

## 📄 License

本项目当前使用 [MIT License](LICENSE)。
