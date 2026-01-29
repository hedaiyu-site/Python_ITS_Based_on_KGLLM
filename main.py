from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入路由（暂时使用空的路由文件，后续会实现）
from routers import auth_router, knowledge_router, learning_router
from routers import chat_router, code_router, recommend_router, system_router

# 创建FastAPI应用实例
app = FastAPI(
    title="毕设后端API服务",
    description="基于FastAPI的智能学习系统后端",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router.router, prefix="/api/auth", tags=["认证"])
app.include_router(knowledge_router.router, prefix="/api/knowledge", tags=["知识查询"])
app.include_router(learning_router.router, prefix="/api/learning", tags=["学习路径"])
app.include_router(chat_router.router, prefix="/api/chat", tags=["智能问答"])
app.include_router(code_router.router, prefix="/api/code", tags=["代码辅助"])
app.include_router(recommend_router.router, prefix="/api/recommend", tags=["个性化推荐"])
app.include_router(system_router.router, prefix="/api/system", tags=["系统监控"])

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "服务运行正常"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)