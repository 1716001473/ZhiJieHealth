# -*- coding: utf-8 -*-
"""
用户收藏关系表
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.connection import Base


class UserFavorite(Base):
    """用户-食谱收藏关系表"""
    __tablename__ = "user_favorite"
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_user_recipe"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    recipe_id = Column(Integer, ForeignKey("premium_recipes.id", ondelete="CASCADE"), nullable=False, comment="食谱ID")
    created_at = Column(DateTime, default=datetime.now, comment="收藏时间")

    def __repr__(self):
        return f"<UserFavorite(user_id={self.user_id}, recipe_id={self.recipe_id})>"
