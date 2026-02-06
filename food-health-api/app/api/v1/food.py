# -*- coding: utf-8 -*-
"""
食物信息 API 路由
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.food_service import FoodService
from app.services.openfoodfacts_service import off_service
from app.schemas.response import APIResponse
from app.schemas.food import (
    FoodResponse, CookingMethodResponse, PortionResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/food/{name}", response_model=APIResponse[FoodResponse])
async def get_food_detail(
    name: str,
    db: Session = Depends(get_db),
):
    """
    获取食物详情
    
    根据食物名称查询详细信息，包括营养数据和禁忌信息
    
    - **name**: 食物名称（如：宫保鸡丁、番茄炒蛋）
    """
    food_service = FoodService(db)
    food = food_service.get_food_response(name)
    
    if not food:
        raise HTTPException(status_code=404, detail=f"未找到食物: {name}")
    
    return APIResponse.success(data=food)


@router.get("/food", response_model=APIResponse[List[FoodResponse]])
async def search_foods(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(default=10, ge=1, le=50, description="返回数量"),
    include_off: bool = Query(default=True, description="是否包含 Open Food Facts 数据"),
    db: Session = Depends(get_db),
):
    """
    搜索食物

    根据关键词搜索食物，返回匹配的食物列表
    当本地数据库结果不足时，自动从 Open Food Facts 获取补充数据

    - **keyword**: 搜索关键词
    - **limit**: 返回数量限制（默认10，最大50）
    - **include_off**: 是否包含 Open Food Facts 数据（默认 true）
    """
    food_service = FoodService(db)

    # 1. 先从本地数据库搜索
    local_foods = food_service.search_foods(keyword, limit)

    # 2. 如果本地结果不足且启用 OFF，从 Open Food Facts 补充
    if include_off and len(local_foods) < limit:
        remaining = limit - len(local_foods)
        local_names = {f.name.lower() for f in local_foods}

        try:
            off_results = await off_service.search_foods(keyword, remaining + 5)

            for off_item in off_results:
                if len(local_foods) >= limit:
                    break

                # 跳过已存在的食物
                if off_item["name"].lower() in local_names:
                    continue

                # 缓存到临时表
                nutrition = {
                    "calories": off_item["calories"],
                    "protein": off_item["protein"],
                    "fat": off_item["fat"],
                    "carb": off_item["carbohydrate"],
                }
                food_service.upsert_temp_food(
                    name=off_item["name"],
                    nutrition=nutrition,
                    source="openfoodfacts"
                )

                # 构建响应
                from app.schemas.food import NutritionInfo
                off_response = FoodResponse(
                    id=0,
                    name=off_item["name"],
                    alias=off_item.get("original_name"),
                    category="Open Food Facts",
                    health_rating="适量",
                    health_tips=None,
                    nutrition=NutritionInfo(
                        calories=off_item["calories"],
                        protein=off_item["protein"],
                        fat=off_item["fat"],
                        carbohydrate=off_item["carbohydrate"],
                        fiber=off_item.get("fiber"),
                        sodium=off_item.get("sodium"),
                        sugar=off_item.get("sugar"),
                    ),
                    serving_desc=None,
                    serving_weight=100,
                    contraindications=[],
                    data_source="openfoodfacts",
                    is_temp=True,
                    image_url=off_item.get("image_url"),
                )
                local_foods.append(off_response)
                local_names.add(off_item["name"].lower())

        except Exception as e:
            logger.warning(f"Open Food Facts 搜索失败: {e}")

    return APIResponse.success(data=local_foods)


@router.get("/cooking-methods", response_model=APIResponse[List[CookingMethodResponse]])
async def get_cooking_methods(db: Session = Depends(get_db)):
    """
    获取所有烹饪方式
    
    返回可用的烹饪方式列表，用于卡路里计算时的用户选择
    """
    food_service = FoodService(db)
    methods = food_service.get_all_cooking_methods()
    
    return APIResponse.success(data=methods)


@router.get("/portions", response_model=APIResponse[List[PortionResponse]])
async def get_portions(db: Session = Depends(get_db)):
    """
    获取所有份量选项
    
    返回可用的份量选项列表，用于卡路里计算时的用户选择
    """
    food_service = FoodService(db)
    portions = food_service.get_all_portions()
    
    return APIResponse.success(data=portions)
