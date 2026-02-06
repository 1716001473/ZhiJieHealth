# -*- coding: utf-8 -*-
"""
创建体重记录表的脚本
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database.connection import Base, engine
from app.models.weight_record import WeightRecord

def create_weight_table():
    """创建体重记录表"""
    print("开始创建体重记录表...")

    # 创建表
    Base.metadata.create_all(bind=engine, tables=[WeightRecord.__table__])

    print("体重记录表创建成功！")
    print(f"表名: {WeightRecord.__tablename__}")
    print(f"字段: id, user_id, weight, record_date, created_at")

if __name__ == "__main__":
    create_weight_table()
