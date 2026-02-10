# -*- coding: utf-8 -*-
"""
用户收藏相关 Schema
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class FavoriteRecipeItem(BaseModel):
    """收藏列表中的食谱项"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None
    cook_time: Optional[str] = None
    difficulty: Optional[str] = None
    favorite_count: int = 0
    favorited_at: Optional[datetime] = None


class FavoriteListResponse(BaseModel):
    """收藏列表响应"""
    items: List[FavoriteRecipeItem] = []
    total: int = 0
    page: int = 1
    page_size: int = 10
    total_pages: int = 0


class FavoriteStatusResponse(BaseModel):
    """收藏状态响应"""
    is_favorited: bool = False
    favorite_count: int = 0
