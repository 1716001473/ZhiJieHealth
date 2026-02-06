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
    # 百度返回的热量（每100g）
    baidu_calorie: Optional[str] = Field(None, description="百度返回的热量")


class RecognitionTopResult(BaseModel):
    """识别结果详情（包含营养信息）"""
    name: str
    confidence: float
    category: Optional[str] = None
    
    # 百度返回的热量（作为补充数据）
    baidu_calorie: Optional[str] = Field(None, description="百度返回的热量(每100g)")
    
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


class RecognizeResponse(BaseModel):
    """识别接口响应"""
    results: List[RecognitionResult] = Field(description="识别结果列表，按置信度排序")
    top_result: Optional[RecognitionTopResult] = Field(None, description="最佳匹配结果详情")
    
    # 提示信息
    message: Optional[str] = None
    is_mock: bool = Field(default=False, description="是否为模拟数据")
