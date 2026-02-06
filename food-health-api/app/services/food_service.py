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
            contraindications=contraindications,
            data_source="database",
            is_temp=False,
        )

    def _build_temp_response(self, temp: FoodTemp) -> FoodResponse:
        nutrition = NutritionInfo(
            calories=temp.calories,
            protein=temp.protein,
            fat=temp.fat,
            carbohydrate=temp.carbohydrate,
        )
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
        """搜索食物"""
        foods = self.db.query(Food).filter(
            (Food.name.contains(keyword)) | (Food.alias.contains(keyword))
        ).limit(limit).all()

        results: List[FoodResponse] = []
        seen_names = set()
        for item in foods:
            response = self.get_food_response(item.name)
            if response:
                results.append(response)
                seen_names.add(response.name)

        temp_foods = self.db.query(FoodTemp).filter(
            FoodTemp.name.contains(keyword)
        ).limit(limit).all()

        for temp in temp_foods:
            if temp.name in seen_names:
                continue
            results.append(self._build_temp_response(temp))
            seen_names.add(temp.name)

        return results[:limit]
