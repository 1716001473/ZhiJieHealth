# -*- coding: utf-8 -*-
"""
识别相关 Pydantic Schema
"""
from typing import Optional, List
from pydantic import BaseModel, Field

from app.schemas.food import NutritionInfo, ContraindicationInfo


class RecognitionResult(BaseModel):
    """单个识别结果"""
    name: str = Field(description="菜品名称")
    confidence: float = Field(description="置信度 0-1")
    category: Optional[str] = Field(None, description="分类")
    food_state: Optional[str] = Field(None, description="食物状态: raw=生食材, cooked=熟菜品")
    
    # 百度返回的热量（每100g）- 兼容旧字段
    baidu_calorie: Optional[str] = Field(None, description="百度返回的热量")
    
    # 豆包返回的丰富信息
    cooking_method: Optional[str] = Field(None, description="烹饪方式")
    estimated_weight: Optional[int] = Field(None, description="估算重量(克)")
    calories_per_100g: Optional[float] = Field(None, description="每100g热量")
    total_calories_min: Optional[int] = Field(None, description="总热量下限")
    total_calories_max: Optional[int] = Field(None, description="总热量上限")
    nutrition: Optional[dict] = Field(None, description="营养信息 {protein, fat, carbohydrate}")
    health_tips: Optional[str] = Field(None, description="健康建议")
    analysis: Optional[str] = Field(None, description="分析说明")
    ai_source: Optional[str] = Field(None, description="AI来源(doubao/baidu/mock)")
    
    # 不适宜人群
    contraindications: Optional[List[dict]] = Field(None, description="不适宜人群列表")


class RecognitionTopResult(BaseModel):
    """识别结果详情（包含营养信息）"""
    name: str
    confidence: float
    category: Optional[str] = None
    food_state: Optional[str] = Field(None, description="食物状态: raw=生食材, cooked=熟菜品")
    
    # 百度返回的热量（作为补充数据）
    baidu_calorie: Optional[str] = Field(None, description="百度返回的热量(每100g)")
    
    # 豆包返回的热量估算
    cooking_method: Optional[str] = Field(None, description="烹饪方式")
    estimated_weight: Optional[int] = Field(None, description="估算重量(克)")
    calories_per_100g: Optional[float] = Field(None, description="每100g热量")
    total_calories_min: Optional[int] = Field(None, description="总热量下限")
    total_calories_max: Optional[int] = Field(None, description="总热量上限")
    analysis: Optional[str] = Field(None, description="AI分析说明")
    
    # 营养信息
    nutrition: Optional[NutritionInfo] = None
    
    # 血糖生成指数 (GI)
    gi: Optional[float] = Field(None, description="血糖生成指数 0-100")
    
    # 健康信息
    health_rating: Optional[str] = None
    health_tips: Optional[str] = None
    
    # 禁忌信息
    contraindications: List[ContraindicationInfo] = []
    
    # 数据来源标记
    found_in_database: bool = False
    ai_generated: bool = Field(default=False, description="是否由AI生成")
    ai_source: Optional[str] = Field(None, description="AI来源(doubao/baidu/deepseek)")


class RecognizeResponse(BaseModel):
    """识别接口响应"""
    results: List[RecognitionResult] = Field(description="识别结果列表，按置信度排序")
    top_result: Optional[RecognitionTopResult] = Field(None, description="最佳匹配结果详情")
    
    # 图片 URL（保存后的服务器路径）
    image_url: Optional[str] = Field(None, description="识别图片 URL")
    
    # 提示信息
    message: Optional[str] = None
    is_mock: bool = Field(default=False, description="是否为模拟数据")

