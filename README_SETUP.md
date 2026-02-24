# 环境配置完成指引

我已经为你搭建好了项目的基础骨架和后端环境。由于我无法直接修改你的系统级安装，请你完成以下最后两步关键操作，即可启动项目。

## 1. ⚠️ 必装软件 (系统级)

请务必安装以下两个软件，否则项目无法运行：

1.  **Node.js (LTS版本)**
    *   **下载地址**: [https://nodejs.org/](https://nodejs.org/)
    *   **用途**: 用于安装和运行前端 (Vue 3) 代码。
    *   *验证*: 安装后新建终端运行 `node -v` 和 `npm -v`。

2.  **Docker Desktop**
    *   **下载地址**: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
    *   **用途**: 用于运行数据库 (PostgreSQL)、缓存 (Redis) 和 C++ 代码沙箱。
    *   *验证*: 安装后启动 Docker Desktop，并在终端运行 `docker -v`。

---

## 2. 🚀 下一步操作

当你安装完上述软件后，请回到本项目根目录，按顺序执行以下命令：

### A. 完成前端安装
```powershell
cd frontend
npm install
```

### B. 启动基础设施 (数据库 & Redis)
```powershell
# 在根目录 (cpp-edu-agent) 下执行
docker-compose up -d
```

### C. 启动后端服务
```powershell
# 在根目录 (cpp-edu-agent) 下执行
.\backend\venv\Scripts\python -m uvicorn backend.main:app --reload
```
访问 http://127.0.0.1:8000/docs 查看接口文档。

### D. 准备 C++ 沙箱镜像
```powershell
docker pull gcc:latest
```

---

## ✅ 已完成的工作
*   [x] 创建后端目录 `backend`
*   [x] 创建前端目录 `frontend`
*   [x] 创建数据库编排文件 `docker-compose.yml`
*   [x] 配置 Python 虚拟环境 `backend/venv`
*   [x] 安装 Python 所有依赖库 (FastAPI, SQLModel, Docker SDK 等)
*   [x] 编写后端入口测试文件 `backend/main.py`
