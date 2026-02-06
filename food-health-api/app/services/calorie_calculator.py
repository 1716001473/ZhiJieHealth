# -*- coding: utf-8 -*-
"""
卡路里计算服务
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.services.food_service import FoodService
from app.schemas.food import CalorieCalculateResponse


class CalorieCalculator:
    """卡路里计算器"""
    
    # 默认浮动范围（±15%）
    FLUCTUATION_PERCENT = 0.15
    
    def __init__(self, db: Session):
        self.db = db
        self.food_service = FoodService(db)
    
    def calculate(
        self,
        food_name: str,
        portion: str = "中份",
        cooking_method: str = "少油炒",
    ) -> Optional[CalorieCalculateResponse]:
        """
        计算卡路里
        
        公式：最终热量 = 基础热量(每100g) × 份量重量(g) / 100 × 烹饪系数 ± 浮动范围
        
        Args:
            food_name: 食物名称
            portion: 份量（小份/中份/大份）
            cooking_method: 烹饪方式
            
        Returns:
            卡路里计算结果
        """
        # 1. 获取食物信息
        food_response = self.food_service.get_food_response(food_name)
        if not food_response or not food_response.nutrition:
            return None
        
        base_calories = food_response.nutrition.calories
        
        # 2. 获取份量信息
        portion_info = self.food_service.get_portion_by_name(portion)
        if portion_info:
            portion_weight = portion_info.weight_grams or 200
            portion_factor = portion_info.calorie_factor or 1.0
        else:
            # 默认中份
            portion_weight = 200
            portion_factor = 1.0
        
        # 3. 获取烹饪方式调整
        cooking_info = self.food_service.get_cooking_method_by_name(cooking_method)
        if cooking_info:
            calorie_adjust = cooking_info.calorie_adjust or 0
            cooking_percent = cooking_info.calorie_percent or 0
        else:
            calorie_adjust = 0
            cooking_percent = 0
        
        # 4. 计算基础热量
        # 基础热量 = 每100g热量 × 份量重量 / 100
        raw_calories = base_calories * portion_weight / 100
        
        # 5. 应用烹饪方式调整
        # 烹饪调整 = 基础热量 × 烹饪百分比 + 固定调整值
        cooking_adjustment = raw_calories * (cooking_percent / 100) + calorie_adjust
        adjusted_calories = raw_calories + cooking_adjustment
        
        # 6. 计算浮动范围
        fluctuation = adjusted_calories * self.FLUCTUATION_PERCENT
        calories_min = int(adjusted_calories - fluctuation)
        calories_max = int(adjusted_calories + fluctuation)
        
        # 确保最小值不为负
        calories_min = max(0, calories_min)
        
        # 7. 构建返回结果
        return CalorieCalculateResponse(
            food_name=food_name,
            base_calories=base_calories,
            portion_weight=portion_weight,
            portion_factor=portion_factor,
            cooking_adjust=calorie_adjust,
            calories_min=calories_min,
            calories_max=calories_max,
            calories_display=f"{calories_min}~{calories_max} kcal",
            breakdown={
                "base": f"{base_calories} kcal/100g × {portion_weight}g = {raw_calories:.0f} kcal",
                "cooking_adjust": f"+{cooking_adjustment:.0f} kcal ({cooking_method})" if cooking_adjustment >= 0 else f"{cooking_adjustment:.0f} kcal ({cooking_method})",
                "range_reason": f"根据实际用油量和配料比例，热量可能在 ±{int(self.FLUCTUATION_PERCENT * 100)}% 范围内浮动",
            }
        )
