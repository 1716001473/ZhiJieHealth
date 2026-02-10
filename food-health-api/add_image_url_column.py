# -*- coding: utf-8 -*-
"""
数据库迁移脚本：为 meal_record 表添加 image_url 列
"""
import sqlite3
import os

def migrate():
    """添加 image_url 列到 meal_record 表"""
    db_path = os.path.join(os.path.dirname(__file__), "food_health.db")

    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查列是否已存在
        cursor.execute("PRAGMA table_info(meal_record)")
        columns = [col[1] for col in cursor.fetchall()]

        if "image_url" in columns:
            print("image_url 列已存在，无需迁移")
            return True

        # 添加新列
        cursor.execute("""
            ALTER TABLE meal_record
            ADD COLUMN image_url VARCHAR(500) NULL
        """)

        conn.commit()
        print("成功添加 image_url 列到 meal_record 表")
        return True

    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
