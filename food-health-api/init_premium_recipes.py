import sys
import os
import json
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.connection import SessionLocal
from app.models.food import PremiumRecipe

def init_data():
    db = SessionLocal()
    
    recipes = [
        {
            "name": "虾仁芦笋全麦意面",
            "description": "低脂高蛋白虾仁搭配高纤维全麦意面，适合减脂期的一餐。",
            "image_url": "/static/uploads/shrimp_pasta.jpg", # 这里暂时指向一个假设的图片，前端会回退到默认图
            "category": "午餐",
            "tags": json.dumps(["均衡饮食", "简单", "15分钟", "减脂", "高蛋白"]),
            "cook_time": "15分钟",
            "prep_time": "10分钟",
            "servings": 1,
            "difficulty": "简单",
            "calories": 475,
            "protein": 50.0,
            "fat": 12.0,
            "carbs": 52.0,
            "ingredients": json.dumps([
                {"name": "鲜虾", "amount": "150克"},
                {"name": "全麦意面", "amount": "50克(干重)"},
                {"name": "芦笋", "amount": "100克"},
                {"name": "西兰花", "amount": "100克"},
                {"name": "蒜末", "amount": "2瓣"},
                {"name": "橄榄油", "amount": "10毫升"}
            ], ensure_ascii=False),
            "steps": json.dumps([
                {"text": "全麦意面按包装说明煮熟(约8-10分钟)，捞出备用。", "image_url": ""},
                {"text": "虾仁去壳去虾线，用盐、黑胡椒腌制5分钟。", "image_url": ""},
                {"text": "芦笋去老根切段，西兰花切小朵，焯水断生。", "image_url": ""},
                {"text": "热锅倒入橄榄油，爆香蒜末，放入虾仁炒至变色。", "image_url": ""},
                {"text": "加入焯好的蔬菜和煮好的意面，翻炒均匀，加少许盐和黑胡椒调味即可。", "image_url": ""}
            ], ensure_ascii=False),
            "tips": "煮意面时水里加点盐和橄榄油，面条更劲道且不粘连。",
            "suitable_for": "减脂人群、健身爱好者",
            "not_suitable_for": "海鲜过敏者",
            "is_featured": True
        },
        {
            "name": "菠菜鸡蛋全麦三明治",
            "description": "简单快手的营养早餐，由全麦面包提供优质碳水，鸡蛋提供蛋白质。",
            "image_url": "/static/uploads/sandwich.jpg",
            "category": "早餐",
            "tags": json.dumps(["早餐", "轻食", "增肌", "可以带饭"]),
            "cook_time": "10分钟",
            "prep_time": "5分钟",
            "servings": 1,
            "difficulty": "简单",
            "calories": 320,
            "protein": 18.0,
            "fat": 10.0,
            "carbs": 35.0,
            "ingredients": json.dumps([
                {"name": "全麦吐司", "amount": "2片"},
                {"name": "鸡蛋", "amount": "1个"},
                {"name": "菠菜", "amount": "50克"},
                {"name": "番茄", "amount": "2片"},
                {"name": "低脂芝士片", "amount": "1片"}
            ], ensure_ascii=False),
            "steps": json.dumps([
                {"text": "菠菜焯水挤干水分，鸡蛋煎熟。", "image_url": ""},
                {"text": "一片吐司放上芝士片、煎蛋、菠菜和番茄片。", "image_url": ""},
                {"text": "盖上另一片吐司，对角切开即可。", "image_url": ""}
            ], ensure_ascii=False),
            "is_featured": True
        },
        {
            "name": "藜麦蔬菜鸡蛋杯",
            "description": "富含全价蛋白的藜麦与多种蔬菜烘烤而成，低卡饱腹。",
            "image_url": "/static/uploads/quinoa_cup.jpg", # 实际也使用默认图
            "category": "早餐",
            "tags": json.dumps(["早餐", "轻食", "控糖", "低脂"]),
            "cook_time": "25分钟",
            "prep_time": "10分钟",
            "servings": 2,
            "difficulty": "简单",
            "calories": 180,
            "protein": 12.0,
            "fat": 6.0,
            "carbs": 20.0,
            "ingredients": json.dumps([
                {"name": "煮熟藜麦", "amount": "100克"},
                {"name": "鸡蛋", "amount": "2个"},
                {"name": "混合蔬菜粒", "amount": "50克"},
                {"name": "牛奶", "amount": "30ml"}
            ], ensure_ascii=False),
            "steps": json.dumps([
                {"text": "鸡蛋打散，加入牛奶、盐和黑胡椒混合。", "image_url": ""},
                {"text": "加入煮熟的藜麦和蔬菜粒搅拌均匀。", "image_url": ""},
                {"text": "倒入模具中，烤箱180度烤20-25分钟。", "image_url": ""}
            ], ensure_ascii=False),
            "is_featured": True
        }
    ]

    try:
        # 清空旧数据（可选，为了演示）
        # db.query(PremiumRecipe).delete()
        
        for data in recipes:
            # 检查是否已存在
            existing = db.query(PremiumRecipe).filter(PremiumRecipe.name == data["name"]).first()
            if not existing:
                recipe = PremiumRecipe(**data)
                db.add(recipe)
                print(f"Adding recipe: {data['name']}")
            else:
                 print(f"Recipe already exists: {data['name']}")
        
        db.commit()
        print("Data initialization completed successfully!")
        
    except Exception as e:
        print(f"Error initializing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_data()
