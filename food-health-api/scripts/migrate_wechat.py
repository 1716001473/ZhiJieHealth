import sys
import os
import logging
from sqlalchemy import text

# 添加项目根目录到 sys.path
sys.path.append(os.getcwd())

from app.database.connection import engine

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_user_table():
    """
    为 user 表添加 openid 和 unionid 字段
    兼容 SQLite 和 MySQL
    """
    logger.info("开始检查 user 表结构...")
    
    with engine.connect() as conn:
        # 获取当前数据库类型
        db_type = engine.dialect.name
        logger.info(f"数据库类型: {db_type}")

        # 检查现有字段
        if db_type == "sqlite":
            result = conn.execute(text("PRAGMA table_info(user)"))
            columns = [row[1] for row in result.fetchall()]
        elif db_type == "mysql":
            result = conn.execute(text("DESCRIBE user"))
            columns = [row[0] for row in result.fetchall()]
        else:
            logger.error(f"不支持的数据库类型: {db_type}")
            return

        # 添加 openid 字段
        if "openid" not in columns:
            logger.info("正在添加 openid 字段...")
            try:
                if db_type == "sqlite":
                    conn.execute(text("ALTER TABLE user ADD COLUMN openid VARCHAR(100)"))
                elif db_type == "mysql":
                    conn.execute(text("ALTER TABLE user ADD COLUMN openid VARCHAR(100) COMMENT '微信 OpenID'"))
                    conn.execute(text("ALTER TABLE user ADD UNIQUE INDEX ix_user_openid (openid)"))
                conn.commit()
                logger.info("openid 字段添加成功")
            except Exception as e:
                logger.error(f"添加 openid 失败: {e}")
        else:
            logger.info("openid 字段已存在")

        # 添加 unionid 字段
        if "unionid" not in columns:
            logger.info("正在添加 unionid 字段...")
            try:
                if db_type == "sqlite":
                    conn.execute(text("ALTER TABLE user ADD COLUMN unionid VARCHAR(100)"))
                elif db_type == "mysql":
                    conn.execute(text("ALTER TABLE user ADD COLUMN unionid VARCHAR(100) COMMENT '微信 UnionID'"))
                    conn.execute(text("ALTER TABLE user ADD UNIQUE INDEX ix_user_unionid (unionid)"))
                conn.commit()
                logger.info("unionid 字段添加成功")
            except Exception as e:
                logger.error(f"添加 unionid 失败: {e}")
        else:
            logger.info("unionid 字段已存在")

    logger.info("迁移完成")

if __name__ == "__main__":
    migrate_user_table()
