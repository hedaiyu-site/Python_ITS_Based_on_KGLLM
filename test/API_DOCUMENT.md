# Python学习助手API文档

## 概述

- **服务名称**: Python学习助手API
- **版本**: 2.0.0
- **描述**: 基于知识图谱+大模型的Python学习系统
- **Base URL**: `http://localhost:8000`
- **交互式文档**: `http://localhost:8000/docs` (Swagger UI)
- **API规范**: `http://localhost:8000/openapi.json`

---

## 通用说明

### 认证方式

部分接口需要JWT Token认证，在请求头中添加：

```
Authorization: Bearer <access_token>
```

### 通用响应格式

#### 成功响应
```json
{
  "success": true,
  "data": { ... }
}
```

#### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "details": { ... }
}
```

### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权/Token无效 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

---

## 接口详情

### 1. 系统接口

#### 1.1 获取服务信息

```
GET /
```

**响应示例**:
```json
{
  "message": "Python学习助手API",
  "version": "2.0.0",
  "status": "running",
  "docs": "/docs"
}
```

#### 1.2 健康检查

```
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

---

### 2. 用户认证模块 `/api/auth`

#### 2.1 用户注册

```
POST /api/auth/register
```

**请求体**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，3-50字符 |
| password | string | 是 | 密码，6-100字符 |
| email | string | 否 | 邮箱地址 |
| learning_path | string | 否 | 学习路径，默认"basic"，可选值：basic, advanced, basic_to_advanced |

**请求示例**:
```json
{
  "username": "testuser",
  "password": "123456",
  "email": "test@example.com",
  "learning_path": "basic"
}
```

**响应示例** (201 Created):
```json
{
  "success": true,
  "message": "注册成功",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "learning_path": "basic",
    "created_at": "2024-01-01T00:00:00",
    "is_active": true
  }
}
```

**错误响应**:
- `422`: 用户名已存在 / 邮箱已被注册 / 参数验证失败

---

#### 2.2 用户登录

```
POST /api/auth/login
```

**请求体**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例**:
```json
{
  "username": "testuser",
  "password": "123456"
}
```

**响应示例** (200 OK):
```json
{
  "success": true,
  "message": "登录成功",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "learning_path": "basic",
    "created_at": "2024-01-01T00:00:00",
    "is_active": true
  }
}
```

**错误响应**:
- `422`: 用户名或密码错误 / 账户已被禁用

---

#### 2.3 获取当前用户信息

```
GET /api/auth/me
```

**认证**: 需要 Bearer Token

**响应示例** (200 OK):
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "learning_path": "basic",
  "created_at": "2024-01-01T00:00:00",
  "is_active": true
}
```

**错误响应**:
- `401`: 无效或过期的token
- `404`: 用户不存在

---

### 3. 对话模块 `/api/chat`

#### 3.1 流式对话

```
POST /api/chat
```

**认证**: 需要 Bearer Token

**请求体**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户消息 |
| context | string | 否 | 可选上下文，默认为空 |
| session_id | string | 否 | 会话ID，不传则创建新会话 |

**请求示例**:
```json
{
  "message": "什么是函数？",
  "context": "",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**响应**:
- Content-Type: `text/event-stream`
- 返回SSE格式的流式数据

**响应格式**:
```
data: {"session_id": "550e8400-e29b-41d4-a716-446655440000"}
data: {"content": "这"}
data: {"content": "是"}
data: {"content": "回"}
data: {"content": "复"}
data: [DONE]
```

**功能说明**:
- 实时返回AI响应
- 自动提取用户问题中的关键词
- 结合知识图谱上下文进行回答
- 支持Python编程相关问题
- 自动保存对话历史记录
- 支持会话连续对话

---

### 4. 聊天历史模块 `/api/history`

#### 4.1 获取会话列表

```
GET /api/history/sessions?limit=20
```

**认证**: 需要 Bearer Token

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | 否 | 返回会话数量限制，默认20 |

**响应示例** (200 OK):
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "什么是函数？",
      "started_at": "2024-01-15T10:30:00",
      "last_message_at": "2024-01-15T10:35:00",
      "message_count": 6
    }
  ]
}
```

---

#### 4.2 获取会话历史

```
GET /api/history/session/{session_id}?limit=50
```

**认证**: 需要 Bearer Token

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话ID |

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | 否 | 返回消息数量限制，默认50 |

**响应示例** (200 OK):
```json
{
  "success": true,
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "什么是函数？",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "函数是Python中的基本概念...",
      "created_at": "2024-01-15T10:30:05"
    }
  ]
}
```

---

#### 4.3 获取最近聊天记录

```
GET /api/history/recent?limit=10
```

**认证**: 需要 Bearer Token

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| limit | int | 否 | 返回消息数量限制，默认10 |

**响应示例** (200 OK):
```json
{
  "success": true,
  "messages": [
    {
      "id": 10,
      "role": "user",
      "content": "谢谢！",
      "created_at": "2024-01-15T10:35:00"
    }
  ]
}
```

---

#### 4.4 删除会话

```
DELETE /api/history/session/{session_id}
```

**认证**: 需要 Bearer Token

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话ID |

**响应示例** (200 OK):
```json
{
  "success": true,
  "message": "会话删除成功"
}
```

**错误响应**:
- `404`: 会话不存在

---

#### 4.5 清空所有聊天记录

```
DELETE /api/history/clear
```

**认证**: 需要 Bearer Token

**响应示例** (200 OK):
```json
{
  "success": true,
  "message": "已清空所有聊天记录",
  "deleted_count": 50
}
```

---

### 5. 知识图谱模块 `/api/kg`

#### 5.1 获取统计信息

```
GET /api/kg/statistics
```

**响应示例** (200 OK):
```json
{
  "success": true,
  "nodes": 100,
  "relations": 200
}
```

---

#### 5.2 获取所有知识点主题

```
GET /api/kg/topics
```

**响应示例** (200 OK):
```json
{
  "success": true,
  "topics": ["函数", "列表", "字典", "类", "模块", "异常", "文件操作"]
}
```

---

#### 5.3 获取课程大纲

```
GET /api/kg/outline/{course_type}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| course_type | string | 是 | 课程类型，可选值：`basic`（基础）、`advanced`（高级） |

**响应示例** (200 OK):
```json
{
  "success": true,
  "course": "Python基础编程教程",
  "chapters": [
    {
      "order": "1",
      "chapter": "Python基础",
      "sections": ["变量", "数据类型", "运算符"]
    },
    {
      "order": "2",
      "chapter": "流程控制",
      "sections": ["if语句", "for循环", "while循环"]
    }
  ]
}
```

**错误响应**:
- `422`: course_type必须为'basic'或'advanced'

---

#### 5.4 获取学习路径

```
GET /api/kg/path/{topic}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| topic | string | 是 | 知识点主题名称 |

**响应示例** (200 OK):
```json
{
  "success": true,
  "paths": [
    {
      "course": "Python基础编程教程",
      "chapter": "Python基础",
      "section": "函数"
    },
    {
      "course": "Python基础编程教程",
      "chapter": "函数进阶",
      "section": "函数参数"
    }
  ]
}
```

---

#### 5.5 搜索知识点

```
GET /api/kg/search/{keyword}
```

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |

**响应示例** (200 OK):
```json
{
  "success": true,
  "context": "【Section】函数\n  - HAS_SECTION: 参数, 返回值\n  - BELONGS_TO: Python基础",
  "learning_paths": [
    {
      "course": "Python基础编程教程",
      "chapter": "Python基础",
      "section": "函数"
    }
  ]
}
```

---

### 6. 学习路径模块 `/api/learning`

#### 6.1 获取用户学习进度

```
GET /api/learning/progress
```

**认证**: 需要 Bearer Token

**响应示例** (200 OK):
```json
{
  "success": true,
  "learning_path": "basic_to_advanced",
  "total_knowledge_points": 100,
  "mastered_count": 20,
  "learning_count": 15,
  "progress_percentage": 20.0,
  "avg_mastery_level": 45.5,
  "knowledge_points": [
    {
      "id": 1,
      "user_id": 1,
      "knowledge_point_id": "course_basic_ch_0_sec_0_kp_0",
      "knowledge_point_name": "Python3简介",
      "course_type": "basic",
      "chapter_name": "一、 Python入门与环境",
      "section_name": "Python语言概述",
      "status": "mastered",
      "mastery_level": 85,
      "quiz_score": 90.0,
      "quiz_count": 5,
      "correct_count": 4,
      "last_study_time": "2024-01-15T10:30:00",
      "created_at": "2024-01-15T10:00:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ]
}
```

**知识点状态说明**:
| 状态 | 说明 |
|------|------|
| not_started | 未开始 |
| learning | 学习中（掌握程度50-79%） |
| mastered | 已掌握（掌握程度>=80%） |
| reviewing | 需复习（掌握程度<50%） |

---

#### 6.2 获取知识点详细进度

```
GET /api/learning/knowledge/{knowledge_point_id}
```

**认证**: 需要 Bearer Token

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| knowledge_point_id | string | 是 | 知识点ID |

**响应示例** (200 OK):
```json
{
  "success": true,
  "message": "",
  "knowledge_point_id": "course_basic_ch_0_sec_0_kp_0",
  "knowledge_point_name": "Python3简介",
  "status": "mastered",
  "mastery_level": 85,
  "quiz_score": 90.0,
  "quiz_count": 5,
  "correct_count": 4,
  "last_study_time": "2024-01-15T10:30:00"
}
```

**错误响应**:
```json
{
  "success": false,
  "message": "知识点进度不存在"
}
```

---

### 7. 测验模块 `/api/quiz`

#### 7.1 获取可测验的知识点列表

```
GET /api/quiz/knowledge-points
```

**认证**: 需要 Bearer Token

**响应示例** (200 OK):
```json
{
  "success": true,
  "knowledge_points": [
    {
      "id": "course_basic_ch_0_sec_0_kp_0",
      "name": "Python3简介",
      "question_count": 10,
      "mastery_level": 85,
      "status": "mastered"
    },
    {
      "id": "course_basic_ch_0_sec_0_kp_1",
      "name": "Python3解释器",
      "question_count": 5,
      "mastery_level": 0,
      "status": "not_started"
    }
  ]
}
```

---

#### 7.2 为知识点生成测验题目--前端不使用这个接口

```
POST /api/quiz/generate/{knowledge_point_id}?knowledge_point_name=xxx&count=10
```

**认证**: 需要 Bearer Token

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| knowledge_point_id | string | 是 | 知识点ID |

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| knowledge_point_name | string | 是 | 知识点名称 |
| count | int | 否 | 生成题目数量，默认10 |

**响应示例** (200 OK):
```json
{
  "success": true,
  "message": "题目生成成功",
  "existing_count": 5,
  "generated_count": 10
}
```

---

#### 7.3 获取知识点测验题目

```
GET /api/quiz/questions/{knowledge_point_id}?count=10
```

**认证**: 需要 Bearer Token

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| knowledge_point_id | string | 是 | 知识点ID |

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| count | int | 否 | 返回题目数量，默认10 |

**响应示例** (200 OK):
```json
{
  "success": true,
  "knowledge_point_id": "course_basic_ch_0_sec_0_kp_0",
  "questions": [
    {
      "id": 1,
      "question": "Python中如何定义函数？",
      "options": ["A. def", "B. function", "C. func", "D. define"],
      "answer": "A"
    },
    {
      "id": 2,
      "question": "Python的创始人是？",
      "options": ["A. James Gosling", "B. Guido van Rossum", "C. Dennis Ritchie", "D. Bjarne Stroustrup"],
      "answer": "B"
    }
  ]
}
```

---

#### 7.4 提交答案

```
POST /api/quiz/submit
```

**认证**: 需要 Bearer Token

**请求体**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| knowledge_point_id | string | 是 | 知识点ID |
| knowledge_point_name | string | 是 | 知识点名称 |
| question_id | int | 是 | 题目ID |
| user_answer | string | 是 | 用户答案（A/B/C/D） |

**请求示例**:
```json
{
  "knowledge_point_id": "course_basic_ch_0_sec_0_kp_0",
  "knowledge_point_name": "Python3简介",
  "question_id": 1,
  "user_answer": "A"
}
```

**响应示例** (200 OK):
```json
{
  "success": true,
  "is_correct": true,
  "correct_answer": "A",
  "explanation": "Python使用def关键字定义函数，这是Python语法的标准定义方式。",
  "your_answer": "A"
}
```

---

#### 7.5 获取知识点测验统计

```
GET /api/quiz/statistics/{knowledge_point_id}
```

**认证**: 需要 Bearer Token

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| knowledge_point_id | string | 是 | 知识点ID |

**响应示例** (200 OK):
```json
{
  "success": true,
  "message": "",
  "quiz_count": 10,
  "correct_count": 8,
  "accuracy": 80.0,
  "mastery_level": 80,
  "recent_history": [
    {
      "question_id": 1,
      "question": "Python中如何定义函数？",
      "user_answer": "A",
      "is_correct": true,
      "quiz_time": "2024-01-15T10:30:00"
    }
  ]
}
```

---

## 数据模型

### UserResponse
```typescript
interface UserResponse {
  id: number;
  username: string;
  email: string | null;
  learning_path: string;  // basic, advanced, basic_to_advanced
  created_at: string;     // ISO 8601 datetime
  is_active: boolean;
}
```

### LoginResponse
```typescript
interface LoginResponse {
  success: boolean;
  message: string;
  access_token: string;
  token_type: string;     // "bearer"
  user: UserResponse;
}
```

### RegisterResponse
```typescript
interface RegisterResponse {
  success: boolean;
  message: string;
  user: UserResponse;
}
```

### ChatRequest
```typescript
interface ChatRequest {
  message: string;
  context?: string;
  session_id?: string;    // 会话ID，不传则创建新会话
}
```

### ChatMessageResponse
```typescript
interface ChatMessageResponse {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}
```

### ChatSessionResponse
```typescript
interface ChatSessionResponse {
  session_id: string;
  title: string;
  started_at: string;
  last_message_at: string;
  message_count: number;
}
```

### SessionListResponse
```typescript
interface SessionListResponse {
  success: boolean;
  sessions: ChatSessionResponse[];
}
```

### SearchResponse
```typescript
interface SearchResponse {
  success: boolean;
  context: string | null;
  learning_paths: LearningPath[];
}

interface LearningPath {
  course: string;
  chapter: string;
  section: string;
}
```

### StatisticsResponse
```typescript
interface StatisticsResponse {
  success: boolean;
  nodes: number;
  relations: number;
}
```

### TopicsResponse
```typescript
interface TopicsResponse {
  success: boolean;
  topics: string[];
}
```

### CourseOutlineResponse
```typescript
interface CourseOutlineResponse {
  success: boolean;
  course: string | null;
  chapters: Chapter[];
}

interface Chapter {
  order: string;
  chapter: string;
  sections: string[];
}
```

### LearningProgressResponse
```typescript
interface LearningProgressResponse {
  success: boolean;
  learning_path: string;
  total_knowledge_points: number;
  mastered_count: number;
  learning_count: number;
  progress_percentage: number;
  avg_mastery_level: number;
  knowledge_points: KnowledgePoint[];
}

interface KnowledgePoint {
  id: number;
  user_id: number;
  knowledge_point_id: string;
  knowledge_point_name: string;
  course_type: string;      // basic, advanced
  chapter_name: string;
  section_name: string;
  status: "not_started" | "learning" | "mastered" | "reviewing";
  mastery_level: number;    // 0-100
  quiz_score: number;
  quiz_count: number;
  correct_count: number;
  last_study_time: string | null;
  created_at: string;
  updated_at: string;
}
```

### KnowledgePointProgressResponse
```typescript
interface KnowledgePointProgressResponse {
  success: boolean;
  message: string;
  knowledge_point_id: string | null;
  knowledge_point_name: string | null;
  status: string | null;
  mastery_level: number | null;
  quiz_score: number | null;
  quiz_count: number | null;
  correct_count: number | null;
  last_study_time: string | null;
}
```

### QuizQuestionResponse
```typescript
interface QuizQuestionResponse {
  id: number;
  question: string;
  options: string[];
  answer: string;
}
```

### QuizQuestionsResponse
```typescript
interface QuizQuestionsResponse {
  success: boolean;
  knowledge_point_id: string;
  questions: QuizQuestionResponse[];
}
```

### SubmitAnswerRequest
```typescript
interface SubmitAnswerRequest {
  knowledge_point_id: string;
  knowledge_point_name: string;
  question_id: number;
  user_answer: string;
}
```

### SubmitAnswerResponse
```typescript
interface SubmitAnswerResponse {
  success: boolean;
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  your_answer: string;
}
```

### QuizStatisticsResponse
```typescript
interface QuizStatisticsResponse {
  success: boolean;
  message: string;
  quiz_count: number;
  correct_count: number;
  accuracy: number;
  mastery_level: number;
  recent_history: QuizHistoryItem[];
}

interface QuizHistoryItem {
  question_id: number;
  question: string;
  user_answer: string;
  is_correct: boolean;
  quiz_time: string;
}
```

### GenerateQuestionsResponse
```typescript
interface GenerateQuestionsResponse {
  success: boolean;
  message: string;
  existing_count: number;
  generated_count: number;
}
```

### QuizKnowledgePointResponse
```typescript
interface QuizKnowledgePointResponse {
  id: string;
  name: string;
  question_count: number;
  mastery_level: number;
  status: string;
}
```

### QuizKnowledgePointsResponse
```typescript
interface QuizKnowledgePointsResponse {
  success: boolean;
  knowledge_points: QuizKnowledgePointResponse[];
}
```

---

## 学习路径类型

| 路径类型 | 名称 | 包含课程 | 预计天数 |
|---------|------|---------|---------|
| basic | 基础学习路径 | course_basic | 30天 |
| advanced | 高级学习路径 | course_advanced | 45天 |
| basic_to_advanced | 完整学习路径 | course_basic + course_advanced | 75天 |

---

## 知识点ID格式

知识点ID采用层级命名格式：
```
course_{type}_ch_{chapter}_sec_{section}_kp_{index}
```

示例：
- `course_basic_ch_0_sec_0_kp_0` - Python3简介
- `course_basic_ch_0_sec_0_kp_1` - Python3解释器
- `course_basic_ch_1_sec_0_kp_0` - 编码、标识符与关键字

---

## 错误码说明

| 错误类型 | 说明 |
|----------|------|
| ValidationError | 数据验证失败 |
| KGConnectionError | 知识图谱连接失败 |
| LLMError | 大模型调用失败 |
| ResourceNotFoundError | 资源不存在 |

---

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
├─────────────────────────────────────────────────────────┤
│  API Layer (Routers)                                    │
│  ├── auth.py          → 用户认证                        │
│  ├── chat.py          → 对话功能                        │
│  ├── history.py       → 聊天历史                        │
│  ├── kg.py            → 知识图谱查询、搜索              │
│  ├── learning_path.py → 学习路径管理                    │
│  └── quiz.py          → 测验功能                        │
├─────────────────────────────────────────────────────────┤
│  Service Layer                                          │
│  ├── UserService           → 用户业务逻辑               │
│  ├── ChatService           → 对话业务逻辑               │
│  ├── ChatHistoryService    → 聊天历史业务逻辑           │
│  ├── KnowledgeGraphService → 知识图谱业务逻辑           │
│  ├── LearningPathService   → 学习路径业务逻辑           │
│  └── QuizService           → 测验业务逻辑               │
├─────────────────────────────────────────────────────────┤
│  Repository Layer                                       │
│  ├── UserRepository (MySQL)        → 用户数据存储       │
│  ├── ChatHistoryRepository (MySQL) → 聊天记录存储       │
│  ├── LearningPathRepository (MySQL)→ 学习进度存储       │
│  └── KnowledgeGraphRepository (Neo4j) → 知识图谱存储    │
├─────────────────────────────────────────────────────────┤
│  AI Layer                                               │
│  └── LLMService (Qwen) → 大模型服务                     │
└─────────────────────────────────────────────────────────┘
```

---

## 数据库表结构

### users 表
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    learning_path VARCHAR(20) DEFAULT 'basic',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### chat_history 表
```sql
CREATE TABLE chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id)
);
```

### knowledge_progress 表
```sql
CREATE TABLE knowledge_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    knowledge_point_id VARCHAR(100) NOT NULL,
    knowledge_point_name VARCHAR(255) NOT NULL,
    course_type VARCHAR(20),
    chapter_name VARCHAR(255),
    section_name VARCHAR(255),
    status ENUM('not_started', 'learning', 'mastered', 'reviewing') DEFAULT 'not_started',
    mastery_level INT DEFAULT 0,
    quiz_score FLOAT DEFAULT 0,
    quiz_count INT DEFAULT 0,
    correct_count INT DEFAULT 0,
    last_study_time TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_kp (user_id, knowledge_point_id)
);
```

### quiz_questions 表
```sql
CREATE TABLE quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    knowledge_point_id VARCHAR(100) NOT NULL,
    knowledge_point_name VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    option_a TEXT NOT NULL,
    option_b TEXT NOT NULL,
    option_c TEXT NOT NULL,
    option_d TEXT NOT NULL,
    correct_answer CHAR(1) NOT NULL,
    explanation TEXT,
    difficulty ENUM('easy', 'medium', 'hard') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### user_quiz_records 表
```sql
CREATE TABLE user_quiz_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    knowledge_point_id VARCHAR(100) NOT NULL,
    question_id INT NOT NULL,
    user_answer CHAR(1) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    quiz_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE
);
```

### learning_path_configs 表
```sql
CREATE TABLE learning_path_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    path_type VARCHAR(20) NOT NULL UNIQUE,
    path_name VARCHAR(100) NOT NULL,
    description TEXT,
    course_ids JSON,
    estimated_days INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 部署说明

### 环境要求
- Python 3.10+
- MySQL 8.0+
- Neo4j 5.0+

### 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m app.main

# 或使用uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 环境变量配置

参考 `.env.example` 文件配置以下环境变量：

```
# Neo4j配置
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# MySQL配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=python_learning

# LLM配置
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-plus

# JWT配置
JWT_SECRET_KEY=your_secret_key
JWT_EXPIRATION_HOURS=24
```

---

## 更新日志

### v2.0.0 (2024-03-20)
- 学习路径知识点细分到最小级别（KnowledgePoint节点）
- 新增 section_name 字段到知识点进度
- 新增获取可测验知识点列表接口
- 优化API文档结构

### v1.3.0 (2024-01-25)
- 删除普通对话接口，统一使用流式对话
- 对话接口路径改为 `POST /api/chat`（流式响应）
- 移除 ChatResponse 数据模型

### v1.2.0 (2024-01-20)
- 删除旧的 learning.py 模块
- 将搜索接口移至知识图谱模块 `/api/kg/search/{keyword}`
- 删除旧的测验接口 `GET /api/quiz/{topic}`
- 统一使用新的测验模块 `/api/quiz`
- 优化API结构，减少模块冗余

### v1.1.0 (2024-01-15)
- 新增聊天历史记录功能
- 新增会话管理接口
- 对话接口支持会话连续性
- 对话接口新增session_id参数
- 新增学习路径管理模块
- 新增测验管理模块

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现用户认证模块
- 实现知识图谱查询功能
- 实现AI对话功能
- 实现学习路径推荐
- 实现测验生成功能
