# -*- coding: utf-8 -*-
"""
精品食谱相关 Schema
"""
import json
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class IngredientItem(BaseModel):
    """食材项 - 兼容多种数据格式"""
    name: str = Field(default="", description="食材名称")
    amount: str = Field(default="", description="用量，如'200g'、'2个'")
    note: Optional[str] = Field(None, description="备注，如'切丁'")

    @field_validator('name', 'amount', mode='before')
    @classmethod
    def ensure_str(cls, v):
        if v is None:
            return ""
        return str(v)


class StepItem(BaseModel):
    """步骤项 - 兼容多种数据格式"""
    step: Optional[int] = Field(None, description="步骤序号")
    content: str = Field(default="", description="步骤说明")
    image_url: Optional[str] = Field(None, description="步骤配图URL")
    tips: Optional[str] = Field(None, description="步骤小贴士")

    @field_validator('step', mode='before')
    @classmethod
    def ensure_int(cls, v):
        if v is None:
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    @field_validator('content', mode='before')
    @classmethod
    def ensure_content_str(cls, v):
        if v is None:
            return ""
        return str(v)


class PremiumRecipeBase(BaseModel):
    """精品食谱基础字段"""
    name: str = Field(..., description="食谱名称", max_length=100)
    description: Optional[str] = Field(None, description="食谱简介")
    image_url: Optional[str] = Field(None, description="主图URL")
    
    # 分类与标签
    category: Optional[str] = Field(None, description="主分类")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    
    # 烹饪信息
    cook_time: Optional[str] = Field(None, description="烹饪时间")
    prep_time: Optional[str] = Field(None, description="准备时间")
    servings: Optional[int] = Field(2, description="份量（几人份）")
    difficulty: Optional[str] = Field("简单", description="难度")
    
    # 营养信息
    calories: Optional[int] = Field(None, description="热量 kcal/份")
    protein: Optional[float] = Field(None, description="蛋白质 g/份")
    fat: Optional[float] = Field(None, description="脂肪 g/份")
    carbs: Optional[float] = Field(None, description="碳水化合物 g/份")
    fiber: Optional[float] = Field(None, description="膳食纤维 g/份")
    sodium: Optional[float] = Field(None, description="钠 mg/份")
    
    # 食材与步骤
    ingredients: Optional[List[IngredientItem]] = Field(default_factory=list, description="食材列表")
    steps: Optional[List[StepItem]] = Field(default_factory=list, description="步骤列表")
    
    # 额外信息
    tips: Optional[str] = Field(None, description="烹饪小贴士")
    suitable_for: Optional[str] = Field(None, description="适合人群")
    not_suitable_for: Optional[str] = Field(None, description="不适合人群")
    
    # 状态
    is_featured: Optional[bool] = Field(False, description="是否精选")
    is_active: Optional[bool] = Field(True, description="是否上架")
    sort_order: Optional[int] = Field(0, description="排序权重")


class PremiumRecipeCreate(PremiumRecipeBase):
    """创建精品食谱"""
    pass


class PremiumRecipeUpdate(BaseModel):
    """更新精品食谱（所有字段可选）"""
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    cook_time: Optional[str] = None
    prep_time: Optional[str] = None
    servings: Optional[int] = None
    difficulty: Optional[str] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None
    fiber: Optional[float] = None
    sodium: Optional[float] = None
    ingredients: Optional[List[IngredientItem]] = None
    steps: Optional[List[StepItem]] = None
    tips: Optional[str] = None
    suitable_for: Optional[str] = None
    not_suitable_for: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class PremiumRecipeResponse(PremiumRecipeBase):
    """精品食谱响应"""
    id: int
    favorite_count: int = 0
    view_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        """将数据库中的 JSON 字符串转为列表"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v or []
    
    @field_validator('ingredients', mode='before')
    @classmethod
    def parse_ingredients(cls, v):
        """将数据库中的 JSON 字符串转为列表，兼容多种格式"""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return []
            except (json.JSONDecodeError, TypeError):
                return []
        if isinstance(v, list):
            return v
        return []

    @field_validator('steps', mode='before')
    @classmethod
    def parse_steps(cls, v):
        """将数据库中的 JSON 字符串转为列表，兼容多种格式"""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    # 兼容纯字符串列表格式 ["步骤1", "步骤2"]
                    result = []
                    for i, item in enumerate(parsed):
                        if isinstance(item, str):
                            result.append({"step": i + 1, "content": item})
                        elif isinstance(item, dict):
                            result.append(item)
                        else:
                            result.append({"step": i + 1, "content": str(item)})
                    return result
                return []
            except (json.JSONDecodeError, TypeError):
                return []
        if isinstance(v, list):
            return v
        return []


class PremiumRecipeListResponse(BaseModel):
    """精品食谱列表响应"""
    items: List[PremiumRecipeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PremiumRecipeListItem(BaseModel):
    """精品食谱列表项（简化版）"""
    id: int
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    cook_time: Optional[str] = None
    difficulty: Optional[str] = None
    calories: Optional[int] = None
    is_featured: bool = False
    favorite_count: int = 0
    
    class Config:
        from_attributes = True
    
    @field_validator('tags', mode='before')
    @classmethod
    def parse_tags(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v or []
