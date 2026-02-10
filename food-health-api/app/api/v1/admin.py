# -*- coding: utf-8 -*-
"""
管理后台 API 路由
提供看板统计、用户管理、食物管理等接口
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.connection import get_db
from app.models.food import Food, PremiumRecipe
from app.models.user import User, RecognitionHistory
from app.schemas.response import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/admin/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    看板统计数据

    返回用户数、食谱数、食物数、分类统计、最新食谱等
    """
    # 基础统计
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_recipes = db.query(func.count(PremiumRecipe.id)).filter(
        PremiumRecipe.is_active == True
    ).scalar() or 0
    total_foods = db.query(func.count(Food.id)).scalar() or 0
    food_categories = db.query(func.count(func.distinct(Food.category))).scalar() or 0

    # 本周新增食谱
    week_ago = datetime.now() - timedelta(days=7)
    week_recipes = db.query(func.count(PremiumRecipe.id)).filter(
        PremiumRecipe.created_at >= week_ago
    ).scalar() or 0

    # 今日识别次数
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_requests = db.query(func.count(RecognitionHistory.id)).filter(
        RecognitionHistory.created_at >= today_start
    ).scalar() or 0

    # 最新食谱（5条）
    latest_recipes_query = db.query(PremiumRecipe).order_by(
        PremiumRecipe.created_at.desc()
    ).limit(5).all()
    latest_recipes = [
        {
            "id": r.id,
            "name": r.name,
            "category": r.category,
            "calories": r.calories,
            "is_featured": r.is_featured,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "",
        }
        for r in latest_recipes_query
    ]

    # 食物分类统计（饼图数据）
    category_stats_query = db.query(
        Food.category, func.count(Food.id).label("count")
    ).group_by(Food.category).all()
    category_stats = [
        {"name": cat or "未分类", "value": count}
        for cat, count in category_stats_query
    ]

    return APIResponse.success(data={
        "total_users": total_users,
        "total_recipes": total_recipes,
        "total_foods": total_foods,
        "food_categories": food_categories,
        "week_recipes": week_recipes,
        "today_requests": today_requests,
        "latest_recipes": latest_recipes,
        "category_stats": category_stats,
    })


@router.get("/admin/users")
async def get_admin_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
):
    """
    管理后台用户列表

    支持分页和关键词搜索（用户名/昵称）
    """
    query = db.query(User)

    if keyword:
        query = query.filter(
            (User.username.like(f"%{keyword}%")) |
            (User.nickname.like(f"%{keyword}%"))
        )

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = [
        {
            "id": u.id,
            "username": u.username,
            "nickname": u.nickname or "",
            "avatar_url": u.avatar_url or "",
            "health_conditions": u.health_conditions or "",
            "health_goal": u.health_goal or "maintain",
            "status": 1,  # 当前模型无 status 字段，默认正常
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if u.created_at else "",
        }
        for u in users
    ]

    return APIResponse.success(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/admin/foods")
async def get_admin_foods(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    db: Session = Depends(get_db),
):
    """
    管理后台食物列表

    支持分页、关键词搜索和分类筛选
    """
    query = db.query(Food)

    if keyword:
        query = query.filter(
            (Food.name.like(f"%{keyword}%")) |
            (Food.alias.like(f"%{keyword}%"))
        )
    if category:
        query = query.filter(Food.category == category)

    total = query.count()
    foods = query.order_by(Food.id.asc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    items = [
        {
            "id": f.id,
            "name": f.name,
            "category": f.category or "",
            "calories": f.calories,
            "protein": f.protein,
            "fat": f.fat,
            "carbohydrate": f.carbohydrate,
            "fiber": f.fiber,
            "health_rating": f.health_rating or "适量",
            "health_tips": f.health_tips or "",
            "created_at": f.created_at.strftime("%Y-%m-%d %H:%M:%S") if f.created_at else "",
        }
        for f in foods
    ]

    # 获取所有分类（供前端筛选下拉框使用）
    categories = [
        row[0] for row in db.query(func.distinct(Food.category)).filter(
            Food.category != None
        ).all()
    ]

    return APIResponse.success(data={
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "categories": categories,
    })
