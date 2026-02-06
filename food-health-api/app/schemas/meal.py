# -*- coding: utf-8 -*-
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict

from app.models.user_meal import MealTypeEnum, DataSourceEnum


class MealRecordBase(BaseModel):
    """饮食记录基础模型"""
    meal_date: date = Field(..., description="记录日期")
    meal_type: MealTypeEnum = Field(..., description="餐次：breakfast, lunch, dinner, snack")
    unit_weight: float = Field(..., gt=0, description="摄入重量（克）")
    note: Optional[str] = Field(None, max_length=200, description="备注")


class MealRecordCreate(MealRecordBase):
    """创建饮食记录请求"""
    food_id: Optional[int] = Field(None, description="关联食物ID，自定义食物可为空")
    food_name: str = Field(..., min_length=1, max_length=100, description="食物名称")
    
    # 可选：如果前端直接传营养数据（如自定义食物），否则后端根据 food_id 查
    per_100g_calories: Optional[float] = Field(None, ge=0)
    per_100g_protein: Optional[float] = Field(None, ge=0)
    per_100g_fat: Optional[float] = Field(None, ge=0)
    per_100g_carb: Optional[float] = Field(None, ge=0)
    
    data_source: DataSourceEnum = Field(default=DataSourceEnum.DATABASE, description="数据来源")


class MealRecordBatchCreate(BaseModel):
    """批量创建饮食记录请求"""
    items: List[MealRecordCreate] = Field(..., description="记录列表")


class MealRecordUpdate(BaseModel):
    """更新饮食记录请求"""
    meal_date: Optional[date] = None
    meal_type: Optional[MealTypeEnum] = None
    unit_weight: Optional[float] = Field(None, gt=0)
    note: Optional[str] = None


class MealRecordResponse(MealRecordBase):
    """饮食记录响应"""
    id: int
    user_id: int
    food_id: Optional[int]
    food_name: str
    
    # 营养快照
    per_100g_calories: float
    per_100g_protein: float
    per_100g_fat: float
    per_100g_carb: float
    
    # 计算值
    calories: float
    protein: float
    fat: float
    carb: float
    
    data_source: DataSourceEnum
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NutritionSummary(BaseModel):
    """营养汇总"""
    calories: float = 0
    protein: float = 0
    fat: float = 0
    carb: float = 0


class DailyNutritionReport(BaseModel):
    """每日营养分析报告"""
    date: date
    total: NutritionSummary
    recommended: NutritionSummary  # 推荐值
    
    # 详情（可选，用于图表）
    protein_pct: float = Field(0, description="蛋白质供能比 %")
    fat_pct: float = Field(0, description="脂肪供能比 %")
    carb_pct: float = Field(0, description="碳水供能比 %")
    
    records: List[MealRecordResponse] = []
