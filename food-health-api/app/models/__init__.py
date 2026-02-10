# -*- coding: utf-8 -*-
"""数据库模型模块"""
from app.models.food import Food, FoodTemp, FoodContraindication, FoodPortion, CookingMethod
from app.models.user import User, RecognitionHistory
from app.models.weight_record import WeightRecord
from app.models.user_favorite import UserFavorite

__all__ = [
    "Food", "FoodTemp", "FoodContraindication", "FoodPortion", "CookingMethod",
    "User", "RecognitionHistory", "WeightRecord",
    "UserFavorite",
]
