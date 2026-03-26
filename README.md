# Python学习助手API

基于知识图谱 + 大模型的智能Python学习系统后端API服务

## 架构设计

项目采用四层架构设计：

```
┌─────────────────────────────────────────────────────────────┐
│                      表现层 (API Layer)                      │
│  ┌─────────────────┐  ┌─────────────────────────────────┐  │
│  │   Routers       │  │         Schemas                 │  │
│  │  - auth.py      │  │  - requests.py (请求模型)        │  │
│  │  - chat.py      │  │  - responses.py (响应模型)       │  │
│  │  - kg.py        │  │                                 │  │
│  │  - learning.py  │  │                                 │  │
│  └────────┬────────┘  └─────────────────────────────────┘  │
└───────────┼─────────────────────────────────────────────────┘
            │
┌───────────┼─────────────────────────────────────────────────┐
│           ▼         业务逻辑层 (Service Layer)               │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  UserService    │  │ KnowledgeGraph  │  ChatService     │
│  │  用户注册/登录   │  │ Service         │  对话/测验生成    │
│  │  JWT认证        │  │ 学习路径推荐     │                  │
│  └────────┬────────┘  └────────┬────────┘  ┌───────┬──────┘
└───────────┼────────────────────┼───────────┼───────┼───────┘
            │                    │           │       │
┌───────────┼────────────────────┼───────────┼───────┼───────┐
│           ▼                    ▼           ▼       │       │
│   数据层 (Repository Layer)              AI服务层         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────┐ │
│  │  UserRepository │  │ KnowledgeGraph  │  │ LLMService │ │
│  │  MySQL用户数据   │  │ Repository      │  │ Qwen大模型  │ │
│  │                 │  │ Neo4j知识图谱    │  │            │ │
│  └────────┬────────┘  └────────┬────────┘  └────────────┘ │
└───────────┼────────────────────┼───────────────────────────┘
            │                    │
            ▼                    ▼
     ┌─────────────┐      ┌─────────────┐
     │   MySQL     │      │   Neo4j     │
     │  用户数据库  │      │  知识图谱    │
     └─────────────┘      └─────────────┘
```

## 项目结构

```
d:\project\RAG\
├── app/
│   ├── __init__.py
│   ├── main.py                     # 应用入口
│   │
│   ├── api/                        # 表现层
│   │   ├── __init__.py
│   │   ├── routers/                # API路由
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # 用户认证路由
│   │   │   ├── chat.py             # 对话路由
│   │   │   ├── kg.py               # 知识图谱路由
│   │   │   └── learning.py         # 学习相关路由
│   │   └── schemas/                # 数据模型
│   │       ├── __init__.py
│   │       ├── requests.py         # 请求模型
│   │       └── responses.py        # 响应模型
│   │
│   ├── services/                   # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py         # 用户业务服务
│   │   ├── kg_service.py           # 知识图谱业务服务
│   │   └── chat_service.py         # 对话业务服务
│   │
│   ├── repositories/               # 数据层
│   │   ├── __init__.py
│   │   ├── mysql/                  # MySQL数据仓库
│   │   │   ├── __init__.py
│   │   │   └── user_repository.py  # 用户数据仓库
│   │   └── neo4j/                  # Neo4j数据仓库
│   │       ├── __init__.py
│   │       └── kg_repository.py    # 知识图谱数据仓库
│   │
│   ├── ai/                         # AI服务层
│   │   ├── __init__.py
│   │   └── llm_service.py          # 大模型服务
│   │
│   └── core/                       # 核心模块
│       ├── __init__.py
│       ├── config.py               # 配置管理
│       ├── dependencies.py         # 依赖注入
│       └── exceptions.py           # 异常处理
│
├── .env                            # 环境配置
├── .env.example                    # 配置示例
├── requirements.txt                # 依赖列表
└── README.md
```

## 功能特性

- **知识图谱查询** - 基于Neo4j的知识图谱存储和查询
- **智能对话** - 集成阿里云Qwen大模型，支持流式输出
- **学习路径推荐** - 根据用户水平个性化推荐学习路径
- **测验生成** - 自动生成Python选择题
- **用户认证** - 用户注册、登录、JWT认证

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，修改配置：

```env
# 应用配置
APP_NAME=Python学习助手API
DEBUG=false

# Neo4j数据库配置
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password
NEO4J_DATABASE=neo4j

# MySQL数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=python_learning

# 大模型配置
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# JWT配置
JWT_SECRET_KEY=your-jwt-secret-key
```

### 3. 启动服务

```bash
# 开发模式
python -m uvicorn app.main:app --reload

# 生产模式
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API接口

### 用户认证模块 (`/auth`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/auth/register` | POST | 用户注册 |
| `/auth/login` | POST | 用户登录，返回JWT token |
| `/auth/me` | GET | 获取当前用户信息（需认证） |

### 对话模块 (`/chat`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/chat` | POST | 普通对话 |
| `/chat/stream` | POST | 流式对话（SSE） |

### 知识图谱模块 (`/kg`)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/kg/statistics` | GET | 知识图谱统计信息 |
| `/kg/topics` | GET | 获取所有知识点主题 |
| `/kg/outline/{course_type}` | GET | 获取课程大纲 |
| `/kg/path/{topic}` | GET | 获取学习路径 |

### 学习模块

| 接口 | 方法 | 说明 |
|------|------|------|
| `/quiz/{topic}` | GET | 生成测验题目 |
| `/search/{keyword}` | GET | 搜索知识点 |

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 技术栈

| 层级 | 技术 |
|------|------|
| 表现层 | FastAPI, Pydantic |
| 业务逻辑层 | Python |
| 数据层 | PyMySQL (MySQL), neo4j-driver (Neo4j) |
| AI服务层 | OpenAI SDK (Qwen兼容) |
| 认证 | JWT |

## License

MIT
