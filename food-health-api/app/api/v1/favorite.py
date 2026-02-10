# -*- coding: utf-8 -*-
"""
用户收藏 API 路由
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.favorite_service import FavoriteService
from app.services.user_service import UserService
from app.schemas.response import APIResponse
from app.schemas.favorite import (
    FavoriteRecipeItem,
    FavoriteListResponse,
    FavoriteStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def require_login(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> int:
    """要求登录，返回用户 ID"""
    if not authorization:
        raise HTTPException(status_code=401, detail="请先登录")
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=401, detail="请先登录")
    user_service = UserService(db)
    user = user_service.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    return user.id


@router.post("/favorites/{recipe_id}")
async def toggle_favorite(
    recipe_id: int,
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """
    切换收藏状态（收藏/取消收藏）

    - 已收藏 → 取消收藏
    - 未收藏 → 添加收藏
    """
    service = FavoriteService(db)
    is_favorited = service.toggle(user_id, recipe_id)
    message = "收藏成功" if is_favorited else "取消收藏成功"
    return APIResponse.success(
        data={"is_favorited": is_favorited},
        message=message,
    )


@router.get("/favorites")
async def get_my_favorites(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """获取当前用户的收藏列表"""
    service = FavoriteService(db)
    items, total = service.get_user_favorites(user_id, page, page_size)
    total_pages = (total + page_size - 1) // page_size

    return APIResponse.success(
        data=FavoriteListResponse(
            items=[FavoriteRecipeItem(**item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
    )


@router.get("/favorites/{recipe_id}/status")
async def get_favorite_status(
    recipe_id: int,
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """查询当前用户对某食谱的收藏状态"""
    service = FavoriteService(db)
    status = service.get_favorite_status(user_id, recipe_id)
    return APIResponse.success(data=status)


@router.get("/favorites/ids")
async def get_favorite_ids(
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """获取当前用户所有收藏的食谱 ID 列表（轻量接口）"""
    service = FavoriteService(db)
    ids = service.get_user_favorite_ids(user_id)
    return APIResponse.success(data=ids)
