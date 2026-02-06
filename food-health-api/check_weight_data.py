# -*- coding: utf-8 -*-
"""
检查体重记录表
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app.database.connection import SessionLocal
from app.models.weight_record import WeightRecord
from app.models.user import User

def check_weight_records():
    """检查体重记录"""
    db = SessionLocal()

    try:
        # 1. 检查表中所有记录
        print("=" * 50)
        print("检查 weight_record 表中的所有记录：")
        print("=" * 50)

        all_records = db.query(WeightRecord).all()
        print(f"总共有 {len(all_records)} 条记录")

        if all_records:
            for record in all_records:
                user = db.query(User).filter(User.id == record.user_id).first()
                username = user.username if user else "未知用户"
                print(f"  - ID: {record.id}, 用户: {username}(ID:{record.user_id}), 体重: {record.weight}kg, 日期: {record.record_date}")
        else:
            print("  (空表)")

        print("\n" + "=" * 50)
        print("检查所有用户：")
        print("=" * 50)

        users = db.query(User).all()
        print(f"总共有 {len(users)} 个用户")
        for user in users:
            print(f"  - ID: {user.id}, 用户名: {user.username}")

    finally:
        db.close()

if __name__ == "__main__":
    check_weight_records()
