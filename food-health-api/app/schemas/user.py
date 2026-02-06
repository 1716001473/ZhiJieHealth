# -*- coding: utf-8 -*-
"""
用户相关 Pydantic Schema
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    health_conditions: List[str] = []
    allergies: List[str] = []
    health_goal: Optional[str] = None
    dietary_preferences: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLoginResponse(BaseModel):
    """登录响应"""
    user: UserResponse
    token: str = Field(description="访问令牌")


class UserUpdateRequest(BaseModel):
    """用户信息更新请求"""
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    health_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    health_goal: Optional[str] = None
    dietary_preferences: Optional[str] = None


class HistoryItemResponse(BaseModel):
    """识别历史项"""
    id: int
    image_url: Optional[str] = None
    recognized_food: str
    confidence: Optional[float] = None
    selected_portion: Optional[str] = None
    selected_cooking: Optional[str] = None
    final_calories_min: Optional[int] = None
    final_calories_max: Optional[int] = None
    result_data: Optional[str] = None  # 完整识别结果JSON
    meal_type: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    """历史列表响应"""
    total: int
    items: List[HistoryItemResponse]


class SaveHistoryRequest(BaseModel):
    """保存历史请求"""
    recognized_food: str = Field(..., description="识别的食物名称")
    confidence: Optional[float] = Field(None, description="置信度")
    selected_portion: Optional[str] = Field(None, description="选择的份量")
    selected_cooking: Optional[str] = Field(None, description="选择的烹饪方式")
    final_calories_min: Optional[int] = Field(None, description="热量下限")
    final_calories_max: Optional[int] = Field(None, description="热量上限")
    result_data: Optional[str] = Field(None, description="完整识别结果JSON")
    meal_type: Optional[str] = Field(None, description="餐次：早餐/午餐/晚餐/加餐")
    note: Optional[str] = Field(None, description="备注")
