# -*- coding: utf-8 -*-
"""Verify food database after import"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import func
from app.database.connection import SessionLocal
from app.models.food import Food

db = SessionLocal()

# 1. Total count
total = db.query(Food).count()
print(f"=== Food table total: {total} ===")

# 2. Search niu nai (milk)
milk_results = db.query(Food).filter(Food.name.contains("\u725b\u5976")).all()
print(f"\nSearch [niu nai]: {len(milk_results)} results")
for f in milk_results[:15]:
    img = "YES" if f.image_url else "NO"
    print(f"  - {f.name} | {f.calories}kcal | img:{img} | {f.category}")

# 3. Search ji dan (egg)
egg_results = db.query(Food).filter(Food.name.contains("\u9e21\u86cb")).all()
print(f"\nSearch [ji dan]: {len(egg_results)} results")
for f in egg_results[:10]:
    img = "YES" if f.image_url else "NO"
    print(f"  - {f.name} | {f.calories}kcal | img:{img} | {f.category}")

# 4. Search mi fan (rice)
rice_results = db.query(Food).filter(Food.name.contains("\u7c73\u996d")).all()
print(f"\nSearch [mi fan]: {len(rice_results)} results")
for f in rice_results[:10]:
    img = "YES" if f.image_url else "NO"
    print(f"  - {f.name} | {f.calories}kcal | img:{img} | {f.category}")

# 5. Image stats
with_img = db.query(Food).filter(Food.image_url.isnot(None), Food.image_url != "").count()
print(f"\n=== Image stats: {with_img}/{total} ({round(with_img/total*100, 1)}%) ===")

# 6. Category distribution
cats = db.query(Food.category, func.count(Food.id)).group_by(Food.category).order_by(func.count(Food.id).desc()).all()
print(f"\n=== Category distribution ===")
for cat, cnt in cats:
    print(f"  {cat}: {cnt}")

db.close()
