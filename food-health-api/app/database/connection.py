# -*- coding: utf-8 -*-
"""
数据库连接配置
"""
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# 创建数据库引擎
# SQLite 需要设置 check_same_thread=False 以支持多线程
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,  # 开发模式下打印 SQL
)

# 创建 Session 工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    """
    获取数据库 Session 的依赖注入函数
    使用 FastAPI 的 Depends 时会自动管理 Session 生命周期
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """创建所有数据库表"""
    # 导入所有模型以确保它们被注册
    from app.models import food, user, user_meal, weight_record, user_favorite  # noqa: F401
    Base.metadata.create_all(bind=engine)


def init_database():
    """初始化数据库（插入初始数据）"""
    from app.database.init_data import init_all_data
    db = SessionLocal()
    try:
        init_all_data(db)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"初始化数据失败: {e}")
    finally:
        db.close()
