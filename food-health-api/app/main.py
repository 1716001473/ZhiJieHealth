# -*- coding: utf-8 -*-
"""
智能食物识别健康助手 - FastAPI 应用入口
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database.connection import create_tables, init_database
from app.api.v1 import recognition, food, calories, user, meal, health, plan

logger = logging.getLogger(__name__)


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时：创建数据库表，初始化数据
    """
    # 启动时执行
    logger.info("正在启动服务...")
    create_tables()
    init_database()
    logger.info("数据库初始化完成")
    
    if settings.baidu_ai_configured:
        logger.info("百度AI已配置")
    else:
        logger.warning("百度AI未配置，识别功能将使用模拟数据")
    
    if settings.deepseek_configured:
        logger.info("DeepSeek AI已配置")
    else:
        logger.warning("DeepSeek未配置，本地无数据时将仅显示百度热量")
    
    yield
    
    # 关闭时执行
    logger.info("服务已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.app_name,
    description="通过摄像头识别食物，获取营养信息和健康建议",
    version=settings.api_version,
    lifespan=lifespan,
)

# 配置 CORS（从配置文件读取允许的来源）
cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册 API 路由
app.include_router(
    recognition.router,
    prefix="/api/v1",
    tags=["食物识别"]
)
app.include_router(
    food.router,
    prefix="/api/v1",
    tags=["食物信息"]
)
app.include_router(
    calories.router,
    prefix="/api/v1",
    tags=["卡路里计算"]
)
app.include_router(
    user.router,
    prefix="/api/v1",
    tags=["用户管理"]
)
app.include_router(
    meal.router,
    prefix="/api/v1/meal",
    tags=["饮食记录"]
)
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["健康建议"]
)
app.include_router(
    plan.router,
    prefix="/api/v1",
    tags=["推荐食谱"]
)


# 挂载静态文件目录（用于头像等资源访问）
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["健康检查"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "app_name": settings.app_name,
        "version": settings.api_version,
        "baidu_ai_configured": settings.baidu_ai_configured,
    }


@app.get("/api/v1/status", tags=["健康检查"])
async def api_status():
    """API 状态接口"""
    return {
        "code": 0,
        "message": "success",
        "data": {
            "status": "running",
            "version": settings.api_version,
            "features": {
                "recognition": settings.baidu_ai_configured,
                "deepseek_configured": settings.deepseek_configured,
                "nutrition": True,
                "calorie_calculation": True,
            }
        }
    }
