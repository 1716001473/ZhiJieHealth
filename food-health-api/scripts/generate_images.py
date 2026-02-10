# -*- coding: utf-8 -*-
"""
为已有食谱批量生成 AI 图片

用法:
    python scripts/generate_images.py                    # 为所有无图食谱生成
    python scripts/generate_images.py --only-missing     # 只为没有图片的食谱生成
    python scripts/generate_images.py --limit 5          # 限制生成数量
"""
import asyncio
import argparse
import sys
import os

# Windows 控制台 UTF-8 编码支持
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.models.food import PremiumRecipe
from app.services.doubao_ai import generate_food_image
from app.config import get_settings


async def main():
    parser = argparse.ArgumentParser(description="AI 菜品图片批量生成")
    parser.add_argument("--only-missing", action="store_true",
                        help="只为没有图片的食谱生成")
    parser.add_argument("--limit", type=int, default=0,
                        help="限制生成数量（0=全部）")
    args = parser.parse_args()

    settings = get_settings()
    if not settings.doubao_api_key:
        print("❌ 豆包AI未配置，请检查 .env 中的 DOUBAO_API_KEY")
        sys.exit(1)

    db = SessionLocal()

    query = db.query(PremiumRecipe).filter(PremiumRecipe.is_active == True)
    if args.only_missing:
        query = query.filter(
            (PremiumRecipe.image_url == None) |
            (PremiumRecipe.image_url == "")
        )

    recipes = query.order_by(PremiumRecipe.id).all()
    if args.limit > 0:
        recipes = recipes[:args.limit]

    print(f"📋 共 {len(recipes)} 道食谱需要生成图片")

    if not recipes:
        print("✅ 没有需要生成图片的食谱")
        db.close()
        return

    success = 0
    failed = 0

    for i, recipe in enumerate(recipes):
        print(f"\n[{i + 1}/{len(recipes)}] 🎨 生成: {recipe.name}...")
        try:
            image_path = await generate_food_image(
                recipe.name, recipe.description or ""
            )
            if image_path:
                recipe.image_url = image_path
                db.commit()
                success += 1
                print(f"  ✅ -> {image_path}")
            else:
                failed += 1
                print(f"  ❌ 生成失败")
        except Exception as e:
            failed += 1
            print(f"  ❌ 错误: {e}")

        # 图片生成 API 限流更严格，间隔 5 秒
        if i < len(recipes) - 1:
            print(f"  ⏳ 等待5秒...")
            await asyncio.sleep(5)

    print(f"\n{'=' * 50}")
    print(f"🎉 完成! 成功: {success}, 失败: {failed}")
    print(f"{'=' * 50}")

    db.close()


if __name__ == "__main__":
    asyncio.run(main())
