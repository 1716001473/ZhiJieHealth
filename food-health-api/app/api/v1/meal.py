# -*- coding: utf-8 -*-
"""
饮食记录 API 路由
"""
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.meal_service import MealService
from app.schemas.response import APIResponse
from app.schemas.meal import (
    MealRecordCreate, 
    MealRecordResponse, 
    MealRecordBatchCreate, 
    MealRecordUpdate,
    DailyNutritionReport
)
# 暂时模拟当前用户ID

router = APIRouter()


@router.post("/record", response_model=APIResponse[MealRecordResponse])
async def create_meal_record(
    request: MealRecordCreate,
    db: Session = Depends(get_db),
    # user_id: int = Depends(get_current_user_id) # 鉴权暂未完全打通，先用模拟
):
    """添加单条饮食记录"""
    # TODO: 替换为真实用户ID获取
    user_id = 1 
    
    service = MealService(db)
    try:
        record = service.create_meal_record(user_id, request)
        return APIResponse.success(data=record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/records/batch", response_model=APIResponse[List[MealRecordResponse]])
async def batch_create_meal_records(
    request: MealRecordBatchCreate,
    db: Session = Depends(get_db),
):
    """批量添加饮食记录"""
    user_id = 1
    service = MealService(db)
    results = []
    try:
        for item in request.items:
            record = service.create_meal_record(user_id, item)
            results.append(record)
        return APIResponse.success(data=results)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/record/{record_id}", response_model=APIResponse[MealRecordResponse])
async def update_meal_record(
    record_id: int,
    request: MealRecordUpdate,
    db: Session = Depends(get_db),
):
    """更新饮食记录"""
    user_id = 1
    service = MealService(db)
    record = service.update_meal_record(record_id, user_id, request)
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在或无权修改")
        
    return APIResponse.success(data=record)


@router.delete("/record/{record_id}", response_model=APIResponse[bool])
async def delete_meal_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    """删除饮食记录"""
    user_id = 1
    service = MealService(db)
    success = service.delete_meal_record(record_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在或无权删除")
        
    return APIResponse.success(data=True)


@router.get("/daily-report", response_model=APIResponse[DailyNutritionReport])
async def get_daily_report(
    date: date = Query(..., description="查询日期"),
    db: Session = Depends(get_db),
):
    """获取每日营养分析报告"""
    user_id = 1
    service = MealService(db)
    report = service.get_daily_report(user_id, date)
    return APIResponse.success(data=report)
