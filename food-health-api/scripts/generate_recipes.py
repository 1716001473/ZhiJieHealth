# -*- coding: utf-8 -*-
"""
AI 食谱批量生成脚本

用法:
    python scripts/generate_recipes.py                  # 生成所有分类
    python scripts/generate_recipes.py --category 早餐  # 只生成指定分类
    python scripts/generate_recipes.py --dry-run        # 只打印不入库
"""
import asyncio
import argparse
import json
import sys
import os

# Windows 控制台 UTF-8 编码支持
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# 将项目根目录加入 sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.models.food import PremiumRecipe
from app.services.recipe_generator import RecipeGenerator, CATEGORIES
from app.schemas.premium_recipe import PremiumRecipeCreate
from app.services.premium_recipe_service import PremiumRecipeService


async def main():
    parser = argparse.ArgumentParser(description="AI 食谱批量生成")
    parser.add_argument("--category", help="只生成指定分类（如：早餐、午餐）")
    parser.add_argument("--dry-run", action="store_true", help="只打印不入库")
    args = parser.parse_args()

    generator = RecipeGenerator()
    if not generator.is_configured:
        print("❌ 豆包AI未配置，请检查 .env 中的 DOUBAO_API_KEY 和 DOUBAO_MODEL")
        sys.exit(1)

    db = SessionLocal()
    service = PremiumRecipeService(db)

    # 获取已有菜名
    existing = db.query(PremiumRecipe.name).all()
    existing_names = [r[0] for r in existing]
    print(f"📋 数据库中已有 {len(existing_names)} 条食谱")

    # 确定要生成的分类
    if args.category:
        if args.category not in CATEGORIES:
            print(f"❌ 未知分类: {args.category}")
            print(f"   可选分类: {', '.join(CATEGORIES.keys())}")
            sys.exit(1)
        categories = {args.category: CATEGORIES[args.category]}
    else:
        categories = CATEGORIES

    total_generated = 0
    total_failed = 0

    for cat_name, cat_info in categories.items():
        count = cat_info["count"]
        print(f"\n{'='*50}")
        print(f"🍳 正在生成 [{cat_name}] 分类 ({count}道)...")
        print(f"{'='*50}")

        try:
            recipes = await generator.generate_recipes_for_category(
                cat_name, count, existing_names
            )

            if not recipes:
                print(f"  ⚠️ 未生成任何食谱")
                total_failed += count
                continue

            for recipe_data in recipes:
                name = recipe_data.get("name", "未知")

                if args.dry_run:
                    print(f"  [DRY-RUN] {name} | {recipe_data.get('calories', 0)} kcal | 标签: {recipe_data.get('tags', [])}")
                    total_generated += 1
                    continue

                # 检查重复
                if name in existing_names:
                    print(f"  [SKIP] {name} 已存在")
                    continue

                try:
                    recipe_create = PremiumRecipeCreate(**recipe_data)
                    service.create(recipe_create)
                    existing_names.append(name)
                    total_generated += 1
                    print(f"  ✅ {name} | {recipe_data.get('calories', 0)} kcal")
                except Exception as e:
                    total_failed += 1
                    print(f"  ❌ {name}: {e}")

        except Exception as e:
            print(f"  ❌ 分类 [{cat_name}] 生成失败: {e}")
            total_failed += count

        # 分类间间隔，避免 API 限流
        if not args.dry_run:
            print(f"  ⏳ 等待2秒...")
            await asyncio.sleep(2)

    print(f"\n{'='*50}")
    print(f"🎉 完成! 成功: {total_generated}, 失败: {total_failed}")
    print(f"{'='*50}")

    db.close()


if __name__ == "__main__":
    asyncio.run(main())
