# -*- coding: utf-8 -*-
"""
批量导入《中国食物成分表第6版》数据到 Food 表
数据源：https://github.com/Sanotsu/china-food-composition-data
"""
import json
import os
import sys
import glob

# 添加项目根目录到 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database.connection import SessionLocal
from app.models.food import Food

# 文件名关键词到分类的映射
FILENAME_CATEGORY_MAP = {
    "谷类": "主食",
    "薯类": "主食",
    "干豆类": "豆制品",
    "蔬菜": "蔬菜",
    "菌藻类": "菌菇",
    "水果": "水果",
    "坚果": "零食",
    "畜肉类": "肉类",
    "禽肉类": "肉类",
    "乳类": "乳制品",
    "蛋类": "蛋类",
    "鱼虾蟹贝": "水产",
    "婴幼儿": "其他",
    "小吃": "零食",
    "速食": "其他",
    "饮料": "饮品",
    "含酒精": "饮品",
    "糖蜜饯": "零食",
    "油脂": "调味品",
    "调味品": "调味品",
    "其他": "其他",
}


def extract_category(filename: str) -> str:
    """从 JSON 文件名提取食物分类"""
    for key, category in FILENAME_CATEGORY_MAP.items():
        if key in filename:
            return category
    return "其他"


def safe_float(value, default=None) -> float:
    """安全转换数值，处理 'Tr'(微量)、'—'(无数据) 等特殊值"""
    if value is None or value == "" or value == "—" or value == "…":
        return default
    if isinstance(value, str):
        if value.lower() == "tr":
            return 0.0
        value = value.strip()
    try:
        return round(float(value), 1)
    except (ValueError, TypeError):
        return default


def clean_name(name: str) -> str:
    """清理食物名称"""
    name = name.strip()
    # 去掉常见后缀
    for suffix in ["(代表值)", "（代表值）", "(均值)", "（均值）"]:
        name = name.replace(suffix, "")
    return name.strip()


def import_single_file(db, filepath: str, category: str, seen_names: set) -> tuple:
    """导入单个 JSON 文件，返回 (added, skipped, errors)"""
    added, skipped, errors = 0, 0, 0

    with open(filepath, "r", encoding="utf-8") as f:
        foods = json.load(f)

    for item in foods:
        food_name = item.get("foodName", "").strip()
        if not food_name:
            errors += 1
            continue

        food_name = clean_name(food_name)
        if not food_name or len(food_name) > 95:
            errors += 1
            continue

        # 内存去重（跨文件同名食物）
        if food_name in seen_names:
            skipped += 1
            continue
        seen_names.add(food_name)

        # 跳过数据库中已存在的
        existing = db.query(Food).filter(Food.name == food_name).first()
        if existing:
            skipped += 1
            continue

        calories = safe_float(item.get("energyKCal"))
        if calories is None:
            errors += 1
            continue

        food = Food(
            name=food_name,
            alias=None,
            category=category,
            calories=calories,
            protein=safe_float(item.get("protein")),
            fat=safe_float(item.get("fat")),
            carbohydrate=safe_float(item.get("CHO")),
            fiber=safe_float(item.get("dietaryFiber")),
            sodium=safe_float(item.get("Na")),
            sugar=None,
            health_rating="适量",
            source="中国食物成分表第6版",
        )
        db.add(food)
        added += 1

    return added, skipped, errors


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "data", "china-food-data", "json_data_vision")

    if not os.path.exists(data_dir):
        print(f"[ERROR] data dir not found: {data_dir}")
        print("please download: git clone --depth 1 https://github.com/Sanotsu/china-food-composition-data.git scripts/data/china-food-data")
        return

    json_files = sorted(glob.glob(os.path.join(data_dir, "merged_*.json")))
    if not json_files:
        print(f"[ERROR] no JSON files found: {data_dir}/merged_*.json")
        return

    print(f"[INFO] found {len(json_files)} JSON files")

    db = SessionLocal()
    total_added, total_skipped, total_errors = 0, 0, 0
    seen_names = set()  # 跨文件去重

    try:
        before_count = db.query(Food).count()
        print(f"-- dao ru qian Food biao ji lu shu: {before_count}")

        for filepath in json_files:
            filename = os.path.basename(filepath)
            category = extract_category(filename)

            added, skipped, errors = import_single_file(db, filepath, category, seen_names)
            total_added += added
            total_skipped += skipped
            total_errors += errors

            if added > 0:
                print(f"  [OK] {filename}: +{added}, skip {skipped}, err {errors} [{category}]")

        db.commit()

        after_count = db.query(Food).count()
        print(f"\n[DONE] Import complete!")
        print(f"   added: {total_added}")
        print(f"   skipped: {total_skipped}")
        print(f"   errors: {total_errors}")
        print(f"   Food table total: {after_count}")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Import failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
