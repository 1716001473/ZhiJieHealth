# -*- coding: utf-8 -*-
"""
从 foodwake 数据集匹配图片 URL 到已有 Food 记录
仅补充 image_url，不导入新食物
数据源：https://github.com/LuckyHookin/foodwake
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database.connection import SessionLocal
from app.models.food import Food


def main():
    data_file = os.path.join(os.path.dirname(__file__), "data", "foodwake", "food-table.json")

    if not os.path.exists(data_file):
        print(f"❌ 数据文件不存在: {data_file}")
        return

    with open(data_file, "r", encoding="utf-8") as f:
        # JSONL 格式：每行一个 JSON 对象
        foodwake_data = []
        for line in f:
            line = line.strip()
            if line:
                try:
                    foodwake_data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    # 构建 foodwake 名称→图片 的映射
    image_map = {}
    for item in foodwake_data:
        name = item.get("name", "").strip()
        img_url = item.get("imgUrl", "").strip()
        if name and img_url:
            image_map[name] = img_url

    print(f"📂 foodwake 数据: {len(image_map)} 条有图片的记录")

    db = SessionLocal()
    try:
        # 查找所有没有图片的 Food 记录
        foods_without_image = db.query(Food).filter(
            (Food.image_url.is_(None)) | (Food.image_url == "")
        ).all()

        print(f"🔍 需要匹配图片的 Food 记录: {len(foods_without_image)} 条")

        updated = 0
        for food in foods_without_image:
            # 精确匹配
            if food.name in image_map:
                food.image_url = image_map[food.name]
                updated += 1
                continue

            # 模糊匹配：foodwake 名称包含 food.name 或反之
            for fw_name, fw_url in image_map.items():
                if len(food.name) >= 2 and (food.name in fw_name or fw_name in food.name):
                    food.image_url = fw_url
                    updated += 1
                    break

        db.commit()
        print(f"\n🎉 图片匹配完成!")
        print(f"   更新: {updated} 条记录")
        print(f"   仍无图片: {len(foods_without_image) - updated} 条")

    except Exception as e:
        db.rollback()
        print(f"❌ 匹配失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
