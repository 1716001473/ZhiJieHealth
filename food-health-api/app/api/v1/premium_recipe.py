# -*- coding: utf-8 -*-
"""
精品食谱 API 路由
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.premium_recipe_service import PremiumRecipeService
from app.schemas.response import APIResponse
from app.schemas.premium_recipe import (
    PremiumRecipeCreate,
    PremiumRecipeUpdate,
    PremiumRecipeResponse,
    PremiumRecipeListResponse,
    PremiumRecipeListItem,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/recipes")
async def get_recipes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    category: Optional[str] = Query(None, description="分类筛选"),
    tag: Optional[str] = Query(None, description="标签筛选"),
    is_featured: Optional[bool] = Query(None, description="是否精选"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
):
    """
    获取精品食谱列表
    
    支持分页、分类筛选、标签筛选、关键词搜索
    """
    service = PremiumRecipeService(db)
    recipes, total = service.get_list(
        page=page,
        page_size=page_size,
        category=category,
        tag=tag,
        is_featured=is_featured,
        keyword=keyword,
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return APIResponse.success(
        data=PremiumRecipeListResponse(
            items=[PremiumRecipeResponse.model_validate(r) for r in recipes],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    )


@router.get("/recipes/featured")
async def get_featured_recipes(
    limit: int = Query(6, ge=1, le=20, description="数量限制"),
    db: Session = Depends(get_db),
):
    """获取精选食谱"""
    service = PremiumRecipeService(db)
    recipes = service.get_featured(limit=limit)
    
    return APIResponse.success(
        data=[PremiumRecipeListItem.model_validate(r) for r in recipes]
    )


@router.get("/recipes/categories")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    service = PremiumRecipeService(db)
    categories = service.get_categories()
    return APIResponse.success(data=categories)


@router.get("/recipes/tags")
async def get_tags(db: Session = Depends(get_db)):
    """获取所有标签"""
    service = PremiumRecipeService(db)
    tags = service.get_tags()
    return APIResponse.success(data=tags)


@router.get("/recipes/{recipe_id}")
async def get_recipe_detail(
    recipe_id: int,
    db: Session = Depends(get_db),
):
    """获取精品食谱详情"""
    service = PremiumRecipeService(db)
    recipe = service.get_by_id(recipe_id)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="食谱不存在")
    
    # 增加浏览数
    service.increment_view_count(recipe_id)
    
    return APIResponse.success(
        data=PremiumRecipeResponse.model_validate(recipe)
    )


@router.post("/recipes")
async def create_recipe(
    recipe_data: PremiumRecipeCreate,
    db: Session = Depends(get_db),
):
    """创建精品食谱"""
    service = PremiumRecipeService(db)
    
    # 检查名称是否重复
    existing = service.get_by_name(recipe_data.name)
    if existing:
        raise HTTPException(status_code=400, detail="食谱名称已存在")
    
    recipe = service.create(recipe_data)
    
    return APIResponse.success(
        data=PremiumRecipeResponse.model_validate(recipe),
        message="食谱创建成功"
    )


@router.put("/recipes/{recipe_id}")
async def update_recipe(
    recipe_id: int,
    recipe_data: PremiumRecipeUpdate,
    db: Session = Depends(get_db),
):
    """更新精品食谱"""
    service = PremiumRecipeService(db)
    
    # 如果更新名称，检查是否重复
    if recipe_data.name:
        existing = service.get_by_name(recipe_data.name)
        if existing and existing.id != recipe_id:
            raise HTTPException(status_code=400, detail="食谱名称已存在")
    
    recipe = service.update(recipe_id, recipe_data)
    
    if not recipe:
        raise HTTPException(status_code=404, detail="食谱不存在")
    
    return APIResponse.success(
        data=PremiumRecipeResponse.model_validate(recipe),
        message="食谱更新成功"
    )


@router.delete("/recipes/{recipe_id}")
async def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
):
    """删除精品食谱"""
    service = PremiumRecipeService(db)
    success = service.delete(recipe_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="食谱不存在")
    
    return APIResponse.success(message="食谱删除成功")


@router.post("/recipes/{recipe_id}/favorite")
async def toggle_favorite(
    recipe_id: int,
    increment: bool = Query(True, description="True=收藏, False=取消收藏"),
    db: Session = Depends(get_db),
):
    """收藏/取消收藏食谱"""
    service = PremiumRecipeService(db)
    
    recipe = service.get_by_id(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="食谱不存在")
    
    service.toggle_favorite(recipe_id, increment=increment)
    
    message = "收藏成功" if increment else "取消收藏成功"
    return APIResponse.success(message=message)
