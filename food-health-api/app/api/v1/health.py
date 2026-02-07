# -*- coding: utf-8 -*-
"""
健康建议 API 路由
"""
from fastapi import APIRouter

from app.schemas.response import APIResponse
from app.schemas.health import HealthAdviceRequest, HealthAdviceResponse
from app.services.deepseek_service import deepseek_service
from app.database.connection import get_db
from app.models.weight_record import WeightRecord
from app.models.user_meal import MealRecord
from app.api.v1.user import get_current_user, require_login
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import Depends
from datetime import date, timedelta, datetime

router = APIRouter()


def calc_bmi(weight: float, height: float) -> float:
    """计算 BMI"""
    if not weight or not height:
        return 0.0
    meters = height / 100
    if not meters:
        return 0.0
    return weight / (meters * meters)


def get_bmi_status(bmi: float) -> str:
    if not bmi:
        return ""
    if bmi < 18.5:
        return "偏低"
    if bmi < 24:
        return "正常"
    if bmi < 28:
        return "超重"
    return "肥胖"


def build_local_advice(payload: HealthAdviceRequest) -> HealthAdviceResponse:
    bmi = calc_bmi(payload.weight or 0, payload.height or 0)
    bmi_value = round(bmi, 1) if bmi else 0
    status = get_bmi_status(bmi_value)

    if not bmi_value:
        diet = "完善健康档案后生成饮食建议"
        exercise = "完善健康档案后生成运动建议"
    elif bmi_value < 18.5:
        diet = "适度提高能量密度，主食与优质蛋白安排在三餐，并可加一份健康加餐。"
        exercise = "以轻中度力量训练为主，避免过量有氧造成能量赤字。"
    elif bmi_value < 24:
        diet = "保持均衡饮食，主食粗细搭配，优先选择优质蛋白与新鲜蔬菜。"
        exercise = "维持规律运动，每周至少 3-5 次中等强度锻炼。"
    elif bmi_value < 28:
        diet = "减少精制碳水与油炸食物，用蔬菜和优质蛋白提高饱腹感。"
        exercise = "增加快走、骑行等中等强度运动，提高每日消耗。"
    else:
        diet = "控制总热量摄入，减少夜宵与含糖饮料，三餐以清淡为主。"
        exercise = "优先循序渐进的有氧运动，搭配力量训练提升基础代谢。"

    return HealthAdviceResponse(
        diet_advice=diet,
        exercise_advice=exercise,
        bmi=bmi_value,
        bmi_status=status,
        source="local",
        ai_generated=False,
    )


@router.post("/health/advice", response_model=APIResponse[HealthAdviceResponse])
async def get_health_advice(payload: HealthAdviceRequest):
    """
    获取健康建议
    
    根据用户健康档案返回饮食与运动建议
    """
    local_advice = build_local_advice(payload)

    if deepseek_service.is_configured:
        ai_advice = await deepseek_service.get_health_advice(payload.model_dump())
        if ai_advice:
            return APIResponse.success(
                HealthAdviceResponse(
                    diet_advice=ai_advice.get("diet_advice", local_advice.diet_advice),
                    exercise_advice=ai_advice.get("exercise_advice", local_advice.exercise_advice),
                    bmi=local_advice.bmi,
                    bmi_status=local_advice.bmi_status,
                    source="deepseek_ai",
                    ai_generated=True,
                )
            )

    return APIResponse.success(local_advice)


@router.post("/health/weight", response_model=APIResponse)
async def add_weight_record(
    payload: HealthAdviceRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    记录体重
    """
    # 未登录用户无法记录
    if not user_id:
        return APIResponse.error(message="请先登录")

    if not payload.weight:
        return APIResponse.error(message="体重不能为空")

    # 查看今日是否已记录,有则更新
    today = date.today()
    record = db.query(WeightRecord).filter(
        WeightRecord.user_id == user_id,
        WeightRecord.record_date == today
    ).first()

    if record:
        record.weight = payload.weight
        record.updated_at = datetime.now()
    else:
        record = WeightRecord(
            user_id=user_id,
            weight=payload.weight,
            record_date=today
        )
        db.add(record)

    db.commit()
    return APIResponse.success(message="体重记录已保存")


@router.get("/health/weight/history", response_model=APIResponse)
async def get_weight_history(
    days: int = 30,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_login)
):
    """获取体重历史趋势"""
    start_date = date.today() - timedelta(days=days)
    records = db.query(WeightRecord).filter(
        WeightRecord.user_id == user_id,
        WeightRecord.record_date >= start_date
    ).order_by(WeightRecord.record_date.asc()).all()

    data = [
        {"date": str(r.record_date), "weight": r.weight}
        for r in records
    ]
    return APIResponse.success(data)


@router.get("/health/nutrition/history", response_model=APIResponse)
async def get_nutrition_history(
    days: int = 7,
    db: Session = Depends(get_db),
    user_id: int = Depends(require_login)
):
    """获取营养摄入趋势"""
    start_date = date.today() - timedelta(days=days)

    # 聚合查询
    results = db.query(
        MealRecord.meal_date,
        func.sum(MealRecord.calories).label("calories"),
        func.sum(MealRecord.protein).label("protein"),
        func.sum(MealRecord.fat).label("fat"),
        func.sum(MealRecord.carb).label("carb")
    ).filter(
        MealRecord.user_id == user_id,
        MealRecord.meal_date >= start_date
    ).group_by(MealRecord.meal_date).order_by(MealRecord.meal_date.asc()).all()

    data = [
        {
            "date": str(r.meal_date),
            "calories": round(r.calories or 0, 1),
            "protein": round(r.protein or 0, 1),
            "fat": round(r.fat or 0, 1),
            "carb": round(r.carb or 0, 1)
        }
        for r in results
    ]
    return APIResponse.success(data)
