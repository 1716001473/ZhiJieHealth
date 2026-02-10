# -*- coding: utf-8 -*-
"""
食物数据库精简脚本
删除第三层冗余数据（中国食物成分表第6版批量导入的~1765条），
保留手工整理的高质量数据，并导入新增的常见单品食物。

使用方法：
    cd food-health-api
    python scripts/slim_food_db.py
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import Settings
from app.models.food import Food, FoodTemp


def get_db_session():
    """获取数据库会话"""
    s = Settings()
    engine = create_engine(s.database_url)
    Session = sessionmaker(bind=engine)
    return Session()


def slim_food_database():
    """精简食物数据库"""
    db = get_db_session()

    try:
        # 1. 统计当前数据
        total_food = db.query(Food).count()
        total_temp = db.query(FoodTemp).count()
        print(f"\n[INFO] 当前数据库状态:")
        print(f"   Food 表: {total_food} 条")
        print(f"   FoodTemp 表: {total_temp} 条")

        # 2. 定义要保留的食物名称（来自 init_data.py + chinese_foods_data.py）
        KEEP_NAMES = [
            # === init_data.py 的 30 条 ===
            "宫保鸡丁", "鱼香肉丝", "红烧肉", "糖醋里脊", "清蒸鱼",
            "水煮牛肉", "回锅肉", "番茄炒蛋", "青椒肉丝", "可乐鸡翅",
            "清炒西兰花", "蒜蓉菠菜", "地三鲜", "醋溜白菜", "麻婆豆腐",
            "白米饭", "馒头", "面条", "饺子", "炒饭",
            "番茄蛋汤", "紫菜蛋花汤", "排骨汤",
            "苹果", "香蕉", "西瓜", "葡萄",
            "豆浆", "酸奶", "薯片",
            # === chinese_foods_data.py 的 57 条 ===
            "娃娃菜", "大白菜", "小白菜", "菠菜", "生菜", "油麦菜",
            "空心菜", "韭菜", "芹菜", "茼蒿",
            "黄瓜", "西红柿", "茄子", "冬瓜", "南瓜", "苦瓜", "丝瓜", "西葫芦",
            "土豆", "红薯", "胡萝卜", "白萝卜", "莲藕", "山药", "芋头",
            "洋葱", "大蒜", "生姜",
            "豆腐", "豆腐干", "豆芽",
            "香菇", "金针菇", "木耳", "平菇", "杏鲍菇",
            "猪肉", "五花肉", "鸡胸肉", "鸡腿肉", "牛肉", "羊肉", "鸭肉",
            "草鱼", "鲫鱼", "带鱼", "虾仁", "基围虾",
            "鸡蛋", "鸭蛋", "牛奶",
            "大米", "小米", "燕麦", "玉米", "红豆", "绿豆",
        ]

        # 3. 删除不在保留列表中的 Food 记录
        foods_to_delete = db.query(Food).filter(~Food.name.in_(KEEP_NAMES)).all()
        delete_count = len(foods_to_delete)

        print(f"\n[DELETE] 准备删除 {delete_count} 条冗余食物数据...")

        if delete_count > 0:
            for food in foods_to_delete:
                db.delete(food)
            db.commit()
            print(f"   [OK] 已删除 {delete_count} 条")

        # 4. 清空 FoodTemp 表
        if total_temp > 0:
            db.query(FoodTemp).delete()
            db.commit()
            print(f"   [OK] 已清空 FoodTemp 表 ({total_temp} 条)")

        # 5. 导入新增的常见单品食物
        print(f"\n[IMPORT] 导入新增常见食物数据...")
        from app.database.common_foods_data import init_common_foods
        init_common_foods(db)

        # 6. 统计最终结果
        final_food = db.query(Food).count()
        final_temp = db.query(FoodTemp).count()

        print(f"\n[RESULT] 精简后数据库状态:")
        print(f"   Food 表: {final_food} 条 (原 {total_food} 条, 减少 {total_food - final_food} 条)")
        print(f"   FoodTemp 表: {final_temp} 条")

        # 分类统计
        categories = db.execute(
            text("SELECT category, COUNT(*) as cnt FROM food GROUP BY category ORDER BY cnt DESC")
        ).fetchall()
        print(f"\n[CATEGORY] 分类统计:")
        for cat, cnt in categories:
            print(f"   {cat}: {cnt} 条")

        print(f"\n[DONE] 数据库精简完成!")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    slim_food_database()
