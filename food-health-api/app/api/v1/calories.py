# -*- coding: utf-8 -*-
"""
卡路里计算 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.calorie_calculator import CalorieCalculator
from app.schemas.response import APIResponse
from app.schemas.food import CalorieCalculateRequest, CalorieCalculateResponse

router = APIRouter()


@router.post("/calculate/calories", response_model=APIResponse[CalorieCalculateResponse])
async def calculate_calories(
    request: CalorieCalculateRequest,
    db: Session = Depends(get_db),
):
    """
    计算卡路里
    
    根据食物名称、份量和烹饪方式，计算预估热量范围
    
    - **food_name**: 食物名称
    - **portion**: 份量（小份/中份/大份）
    - **cooking_method**: 烹饪方式（清蒸/水煮/少油炒/红烧/油炸）
    
    返回：
    - **calories_min**: 热量下限
    - **calories_max**: 热量上限
    - **calories_display**: 显示文本（如 "320~400 kcal"）
    - **breakdown**: 详细计算过程
    """
    calculator = CalorieCalculator(db)
    result = calculator.calculate(
        food_name=request.food_name,
        portion=request.portion,
        cooking_method=request.cooking_method,
    )
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"未找到食物 '{request.food_name}' 的营养信息，无法计算卡路里"
        )
    
    return APIResponse.success(data=result)


@router.get("/calculate/calories/{food_name}", response_model=APIResponse[CalorieCalculateResponse])
async def calculate_calories_simple(
    food_name: str,
    portion: str = "中份",
    cooking_method: str = "少油炒",
    db: Session = Depends(get_db),
):
    """
    计算卡路里（简化版 GET 接口）
    
    使用 URL 参数快速计算卡路里，适合简单场景
    
    - **food_name**: 食物名称（路径参数）
    - **portion**: 份量（查询参数，默认"中份"）
    - **cooking_method**: 烹饪方式（查询参数，默认"少油炒"）
    """
    calculator = CalorieCalculator(db)
    result = calculator.calculate(
        food_name=food_name,
        portion=portion,
        cooking_method=cooking_method,
    )
    
    if not result:
        raise HTTPException(
            status_code=404, 
            detail=f"未找到食物 '{food_name}' 的营养信息"
        )
    
    return APIResponse.success(data=result)
