# -*- coding: utf-8 -*-
"""
食物数据服务
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.food import Food, FoodTemp, FoodContraindication, CookingMethod, FoodPortion
from app.schemas.food import (
    FoodResponse, NutritionInfo, ContraindicationInfo,
    CookingMethodResponse, PortionResponse
)


class FoodService:
    """食物数据服务"""
    
    def __init__(self, db: Session):
        self.db = db

    # ------ 智能单位推断 ------
    # 根据食物分类和名称，自动推断最合适的计量单位
    UNIT_RULES = {
        # category -> (default_unit, unit_weight)
        "水果": ("个", 200),
        "主食": ("碗", 200),
        "饮品": ("杯", 250),
        "汤类": ("碗", 300),
        "零食": ("份", 50),
    }

    # 名称关键词 -> (default_unit, unit_weight)
    KEYWORD_UNITS = {
        # 水果类
        "苹果": ("个", 200), "梨": ("个", 250), "橙": ("个", 200),
        "桃": ("个", 200), "香蕉": ("根", 120), "猕猴桃": ("个", 100),
        "橘": ("个", 100), "柚": ("瓣", 50), "芒果": ("个", 250),
        "葡萄": ("串", 200), "草莓": ("颗", 15), "樱桃": ("颗", 10),
        "荔枝": ("颗", 20), "龙眼": ("颗", 12), "枣": ("颗", 15),
        "柿": ("个", 200), "李": ("个", 60), "杏": ("个", 50),
        "西瓜": ("块", 300), "哈密瓜": ("块", 200),
        # 主食
        "米饭": ("碗", 200), "面条": ("碗", 250), "粥": ("碗", 300),
        "馒头": ("个", 100), "包子": ("个", 100), "饺子": ("个", 20),
        "面包": ("片", 40), "吐司": ("片", 40), "饼": ("张", 80),
        "粽子": ("个", 150), "汤圆": ("个", 25), "烧卖": ("个", 30),
        "春卷": ("个", 50),
        # 蛋类
        "鸡蛋": ("个", 60), "鸭蛋": ("个", 70), "鹌鹑蛋": ("个", 10),
        # 饮品
        "牛奶": ("杯", 250), "豆浆": ("杯", 250), "酸奶": ("杯", 200),
        "咖啡": ("杯", 250), "茶": ("杯", 250), "果汁": ("杯", 250),
        "可乐": ("杯", 330), "啤酒": ("杯", 330),
        # 零食
        "饼干": ("片", 10), "薯片": ("包", 50), "坚果": ("把", 25),
        "巧克力": ("块", 20), "糖果": ("颗", 5),
    }

    def _infer_unit(self, name: str, category: str = None,
                    serving_desc: str = None, serving_weight: int = None):
        """根据食物信息推断智能单位"""
        # 优先使用数据库中已有的 serving 信息
        if serving_desc and serving_weight and serving_weight != 100:
            return serving_desc, serving_weight

        # 按名称关键词匹配
        for keyword, (unit, weight) in self.KEYWORD_UNITS.items():
            if keyword in name:
                return unit, weight

        # 按分类匹配
        if category and category in self.UNIT_RULES:
            return self.UNIT_RULES[category]

        # 默认：按"份"算，100g 一份
        return "份", 100
    
    def get_food_by_name(self, name: str) -> Optional[Food]:
        """根据名称查询食物"""
        # 精确匹配
        food = self.db.query(Food).filter(Food.name == name).first()
        if food:
            return food
        
        # 模糊匹配（别名）
        food = self.db.query(Food).filter(Food.alias.contains(name)).first()
        return food
    
    def get_food_response(self, name: str) -> Optional[FoodResponse]:
        """获取食物详情响应"""
        food = self.get_food_by_name(name)
        if not food:
            return None
        
        # 构建营养信息
        nutrition = NutritionInfo(
            calories=food.calories or 0,
            protein=food.protein or 0,
            fat=food.fat or 0,
            carbohydrate=food.carbohydrate or 0,
            fiber=food.fiber,
            sodium=food.sodium,
            sugar=food.sugar,
        )
        
        # 获取禁忌信息
        contraindications = self._get_contraindications(food)
        
        # 推断智能单位
        default_unit, unit_weight = self._infer_unit(
            food.name, food.category, food.serving_desc, food.serving_weight
        )
        
        return FoodResponse(
            id=food.id,
            name=food.name,
            alias=food.alias,
            category=food.category,
            health_rating=food.health_rating or "适量",
            health_tips=food.health_tips,
            nutrition=nutrition,
            serving_desc=food.serving_desc,
            serving_weight=food.serving_weight or 100,
            default_unit=default_unit,
            unit_weight=unit_weight,
            contraindications=contraindications,
            data_source="database",
            is_temp=False,
            image_url=food.image_url,
        )

    def _build_temp_response(self, temp: FoodTemp) -> FoodResponse:
        nutrition = NutritionInfo(
            calories=temp.calories,
            protein=temp.protein,
            fat=temp.fat,
            carbohydrate=temp.carbohydrate,
        )
        # 推断智能单位
        default_unit, unit_weight = self._infer_unit(temp.name)
        return FoodResponse(
            id=temp.id,
            name=temp.name,
            alias=None,
            category="AI补充",
            health_rating="适量",
            health_tips=None,
            nutrition=nutrition,
            serving_desc=None,
            serving_weight=100,
            default_unit=default_unit,
            unit_weight=unit_weight,
            contraindications=[],
            data_source=temp.source,
            is_temp=True,
        )

    def upsert_temp_food(self, name: str, nutrition: dict, source: str) -> Optional[FoodTemp]:
        """写入临时食物数据（AI/用户补充）"""
        food = self.get_food_by_name(name)
        if food:
            return None

        temp = self.db.query(FoodTemp).filter(FoodTemp.name == name).first()
        calories = nutrition.get("calories", 0) or 0
        protein = nutrition.get("protein", 0) or 0
        fat = nutrition.get("fat", 0) or 0
        carb = nutrition.get("carb", 0) or 0

        if temp:
            temp.calories = calories
            temp.protein = protein
            temp.fat = fat
            temp.carbohydrate = carb
            temp.source = source
        else:
            temp = FoodTemp(
                name=name,
                calories=calories,
                protein=protein,
                fat=fat,
                carbohydrate=carb,
                source=source,
            )
            self.db.add(temp)

        self.db.commit()
        self.db.refresh(temp)
        return temp
    
    def _get_contraindications(self, food: Food) -> List[ContraindicationInfo]:
        """获取食物的禁忌信息"""
        result = []
        
        # 1. 获取直接关联的禁忌
        if food.contraindications:
            for c in food.contraindications:
                result.append(ContraindicationInfo(
                    condition_type=c.condition_type,
                    severity=c.severity,
                    reason=c.reason,
                    suggestion=c.suggestion,
                ))
        
        # 2. 获取关键词匹配的通用禁忌
        food_name = food.name.lower()
        generic_rules = self.db.query(FoodContraindication).filter(
            FoodContraindication.food_id.is_(None),
            FoodContraindication.food_keyword.isnot(None),
        ).all()
        
        for rule in generic_rules:
            if rule.food_keyword and rule.food_keyword.lower() in food_name:
                # 检查是否已存在相同类型的禁忌
                exists = any(c.condition_type == rule.condition_type for c in result)
                if not exists:
                    result.append(ContraindicationInfo(
                        condition_type=rule.condition_type,
                        severity=rule.severity,
                        reason=rule.reason,
                        suggestion=rule.suggestion,
                    ))
        
        return result
    
    def get_all_cooking_methods(self) -> List[CookingMethodResponse]:
        """获取所有烹饪方式"""
        methods = self.db.query(CookingMethod).order_by(CookingMethod.sort_order).all()
        return [
            CookingMethodResponse(
                id=m.id,
                name=m.name,
                calorie_adjust=m.calorie_adjust,
                calorie_percent=m.calorie_percent,
                description=m.description,
                icon=m.icon,
            )
            for m in methods
        ]
    
    def get_cooking_method_by_name(self, name: str) -> Optional[CookingMethod]:
        """根据名称获取烹饪方式"""
        return self.db.query(CookingMethod).filter(CookingMethod.name == name).first()
    
    def get_all_portions(self) -> List[PortionResponse]:
        """获取所有份量选项"""
        portions = self.db.query(FoodPortion).filter(
            FoodPortion.food_id.is_(None)  # 通用份量
        ).order_by(FoodPortion.sort_order).all()
        
        return [
            PortionResponse(
                id=p.id,
                portion_name=p.portion_name,
                weight_grams=p.weight_grams,
                calorie_factor=p.calorie_factor,
                is_default=p.is_default,
            )
            for p in portions
        ]
    
    def get_portion_by_name(self, name: str) -> Optional[FoodPortion]:
        """根据名称获取份量选项"""
        return self.db.query(FoodPortion).filter(FoodPortion.portion_name == name).first()
    
    def search_foods(self, keyword: str, limit: int = 10) -> List[FoodResponse]:
        """搜索食物 - 优化版：精确匹配优先"""
        from sqlalchemy import case, or_

        # 构建优先级排序：精确匹配 > 前缀匹配 > 别名匹配 > 包含匹配
        priority = case(
            (Food.name == keyword, 1),
            (Food.name.startswith(keyword), 2),
            (Food.alias.contains(keyword), 3),
            else_=4
        )

        foods = self.db.query(Food).filter(
            or_(
                Food.name.contains(keyword),
                Food.alias.contains(keyword)
            )
        ).order_by(priority).limit(limit).all()

        results: List[FoodResponse] = []
        seen_names = set()
        for item in foods:
            response = self.get_food_response(item.name)
            if response:
                results.append(response)
                seen_names.add(response.name)

        # FoodTemp 补充
        if len(results) < limit:
            remaining = limit - len(results)
            temp_foods = self.db.query(FoodTemp).filter(
                FoodTemp.name.contains(keyword)
            ).limit(remaining).all()

            for temp in temp_foods:
                if temp.name in seen_names:
                    continue
                results.append(self._build_temp_response(temp))
                seen_names.add(temp.name)

        return results[:limit]
