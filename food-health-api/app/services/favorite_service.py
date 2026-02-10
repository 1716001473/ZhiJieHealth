# -*- coding: utf-8 -*-
"""
用户收藏服务
"""
import logging
from typing import List, Tuple, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.user_favorite import UserFavorite
from app.models.food import PremiumRecipe

logger = logging.getLogger(__name__)


class FavoriteService:
    """用户收藏服务"""

    def __init__(self, db: Session):
        self.db = db

    def is_favorited(self, user_id: int, recipe_id: int) -> bool:
        """查询用户是否已收藏某食谱"""
        return self.db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.recipe_id == recipe_id,
        ).first() is not None

    def toggle(self, user_id: int, recipe_id: int) -> bool:
        """
        切换收藏状态（幂等操作）
        返回 True 表示收藏，False 表示取消收藏
        """
        existing = self.db.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.recipe_id == recipe_id,
        ).first()

        if existing:
            # 取消收藏
            self.db.delete(existing)
            # 减少食谱收藏计数
            self.db.query(PremiumRecipe).filter(
                PremiumRecipe.id == recipe_id,
                PremiumRecipe.favorite_count > 0,
            ).update({"favorite_count": PremiumRecipe.favorite_count - 1})
            self.db.commit()
            return False
        else:
            # 添加收藏
            fav = UserFavorite(user_id=user_id, recipe_id=recipe_id)
            self.db.add(fav)
            # 增加食谱收藏计数
            self.db.query(PremiumRecipe).filter(
                PremiumRecipe.id == recipe_id,
            ).update({"favorite_count": PremiumRecipe.favorite_count + 1})
            self.db.commit()
            return True

    def get_user_favorites(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
    ) -> Tuple[List[dict], int]:
        """
        获取用户收藏列表（分页）
        返回 (收藏食谱列表, 总数)
        """
        query = (
            self.db.query(UserFavorite, PremiumRecipe)
            .join(PremiumRecipe, UserFavorite.recipe_id == PremiumRecipe.id)
            .filter(
                UserFavorite.user_id == user_id,
                PremiumRecipe.is_active == True,
            )
            .order_by(desc(UserFavorite.created_at))
        )

        total = query.count()
        rows = query.offset((page - 1) * page_size).limit(page_size).all()

        items = []
        for fav, recipe in rows:
            items.append({
                "id": recipe.id,
                "name": recipe.name,
                "description": recipe.description,
                "image_url": recipe.image_url,
                "category": recipe.category,
                "calories": recipe.calories,
                "protein": recipe.protein,
                "fat": recipe.fat,
                "carbs": recipe.carbs,
                "cook_time": recipe.cook_time,
                "difficulty": recipe.difficulty,
                "favorite_count": recipe.favorite_count,
                "favorited_at": fav.created_at,
            })

        return items, total

    def get_favorite_status(self, user_id: int, recipe_id: int) -> dict:
        """获取收藏状态和收藏数"""
        is_fav = self.is_favorited(user_id, recipe_id)
        recipe = self.db.query(PremiumRecipe).filter(
            PremiumRecipe.id == recipe_id
        ).first()
        count = recipe.favorite_count if recipe else 0
        return {"is_favorited": is_fav, "favorite_count": count}

    def get_user_favorite_ids(self, user_id: int) -> List[int]:
        """获取用户所有收藏的食谱 ID 列表"""
        rows = self.db.query(UserFavorite.recipe_id).filter(
            UserFavorite.user_id == user_id,
        ).all()
        return [r[0] for r in rows]
