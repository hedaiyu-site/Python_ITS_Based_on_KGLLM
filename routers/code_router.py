from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.code_service import CodeService

router = APIRouter()

# 创建CodeService实例
code_service = CodeService()

# 代码分析相关模型
class CodeAnalyzeRequest(BaseModel):
    code: str
    language: str = "python"

class CodeAnalysis(BaseModel):
    syntax_errors: list[dict]
    style_issues: list[dict]
    complexity_score: float
    suggestions: list[str]

class CodeCorrectRequest(BaseModel):
    code: str
    error_info: dict = None
    language: str = "python"

class CodeGenerateRequest(BaseModel):
    prompt: str
    language: str = "python"
    requirements: str = None

class CodeExplainRequest(BaseModel):
    code: str
    language: str = "python"

# 路由端点
@router.post("/analyze", response_model=CodeAnalysis)
async def analyze_code(request: CodeAnalyzeRequest):
    """代码分析"""
    result = await code_service.analyze(request.code, request.language)
    return CodeAnalysis(
        syntax_errors=result["syntax_errors"],
        style_issues=result["style_issues"],
        complexity_score=result["complexity_score"],
        suggestions=result["suggestions"]
    )

@router.post("/correct")
async def correct_code(request: CodeCorrectRequest):
    """代码纠错"""
    result = await code_service.correct(request.code, request.language, request.error_info)
    return result

@router.post("/generate")
async def generate_code(request: CodeGenerateRequest):
    """代码生成"""
    result = await code_service.generate(request.prompt, request.language, request.requirements)
    return result

@router.post("/explain")
async def explain_code(request: CodeExplainRequest):
    """代码解释"""
    result = await code_service.explain(request.code, request.language)
    return result