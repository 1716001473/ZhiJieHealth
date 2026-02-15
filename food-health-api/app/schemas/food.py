# -*- coding: utf-8 -*-
"""
食物相关 Pydantic Schema
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class NutritionInfo(BaseModel):
    """营养信息"""
    calories: float = Field(description="热量 kcal/100g")
    protein: float = Field(description="蛋白质 g/100g")
    fat: float = Field(description="脂肪 g/100g")
    carbohydrate: float = Field(description="碳水化合物 g/100g")
    fiber: Optional[float] = Field(None, description="膳食纤维 g/100g")
    sodium: Optional[float] = Field(None, description="钠 mg/100g")
    sugar: Optional[float] = Field(None, description="糖 g/100g")


class ContraindicationInfo(BaseModel):
    """禁忌信息"""
    condition_type: str = Field(description="疾病/人群类型")
    severity: str = Field(description="严重程度：禁食/慎食/少食")
    reason: Optional[str] = Field(None, description="原因说明")
    suggestion: Optional[str] = Field(None, description="替代建议")


class FoodBase(BaseModel):
    """食物基础信息"""
    name: str = Field(description="食物名称")
    category: Optional[str] = Field(None, description="分类")
    health_rating: str = Field(default="适量", description="健康评级")
    health_tips: Optional[str] = Field(None, description="健康提示")


class FoodResponse(FoodBase):
    """食物详情响应"""
    id: int
    alias: Optional[str] = None
    data_source: Optional[str] = None
    is_temp: bool = False

    # 营养信息
    nutrition: Optional[NutritionInfo] = None

    # 份量信息
    serving_desc: Optional[str] = None
    serving_weight: int = 100

    # 智能单位（前端用于统一展示）
    default_unit: str = Field(default="g", description="默认计量单位：g/个/碗/杯/片/份")
    unit_weight: int = Field(default=100, description="每单位对应的克数")

    # 禁忌信息
    contraindications: List[ContraindicationInfo] = []

    # 图片
    image_url: Optional[str] = Field(None, description="食物图片 URL")
    
    class Config:
        from_attributes = True


class FoodListResponse(BaseModel):
    """食物列表响应"""
    total: int
    items: List[FoodResponse]


class CookingMethodResponse(BaseModel):
    """烹饪方式响应"""
    id: int
    name: str
    calorie_adjust: int = Field(description="热量调整值 kcal")
    calorie_percent: float = Field(description="热量调整百分比")
    description: Optional[str] = None
    icon: Optional[str] = None
    
    class Config:
        from_attributes = True


class PortionResponse(BaseModel):
    """份量选项响应"""
    id: int
    portion_name: str
    weight_grams: Optional[int] = None
    calorie_factor: float = 1.0
    is_default: bool = False
    
    class Config:
        from_attributes = True


class CalorieCalculateRequest(BaseModel):
    """卡路里计算请求"""
    food_name: str = Field(description="食物名称")
    portion: str = Field(default="中份", description="份量：小份/中份/大份")
    cooking_method: str = Field(default="少油炒", description="烹饪方式")


class CalorieCalculateResponse(BaseModel):
    """卡路里计算响应"""
    food_name: str
    base_calories: float = Field(description="每100g基础热量")
    portion_weight: int = Field(description="估算重量 g")
    portion_factor: float = Field(description="份量系数")
    cooking_adjust: int = Field(description="烹饪方式调整值")
    
    calories_min: int = Field(description="热量下限 kcal")
    calories_max: int = Field(description="热量上限 kcal")
    calories_display: str = Field(description="显示文本，如 '320~400 kcal'")
    
    breakdown: dict = Field(description="计算详情")
