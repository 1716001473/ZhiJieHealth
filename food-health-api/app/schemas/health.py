# -*- coding: utf-8 -*-
from typing import Optional
from pydantic import BaseModel, Field


class HealthAdviceRequest(BaseModel):
    """健康建议请求"""
    weight: Optional[float] = Field(None, ge=0, description="体重(kg)")
    height: Optional[float] = Field(None, ge=0, description="身高(cm)")
    age: Optional[int] = Field(None, ge=0, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    activity: Optional[str] = Field(None, description="活动水平")


class HealthAdviceResponse(BaseModel):
    """健康建议响应"""
    diet_advice: str = Field(..., description="饮食建议")
    exercise_advice: str = Field(..., description="运动建议")
    bmi: float = Field(0, description="BMI 数值")
    bmi_status: str = Field("", description="BMI 状态")
    source: str = Field("local", description="建议来源")
    ai_generated: bool = Field(False, description="是否 AI 生成")
