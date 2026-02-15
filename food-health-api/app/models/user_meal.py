# -*- coding: utf-8 -*-
"""
饮食记录模型（MealRecord）

此模型在原有 `MealRecord` 基础上进行优化，增加了营养数据快照、数据来源标记、约束与索引等，以确保历史记录的可靠性和查询性能。
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum as SqlEnum, Index, Text, ForeignKey

from app.database.connection import Base


class MealTypeEnum(str, Enum):
    """餐次枚举，统一存储值"""
    BREAKFAST = "breakfast"  # 早餐
    LUNCH = "lunch"          # 午餐
    DINNER = "dinner"        # 晚餐
    SNACK = "snack"          # 加餐


class DataSourceEnum(str, Enum):
    """营养数据来源枚举"""
    DATABASE = "database"      # 来自本地食物库
    DEEPSEEK_AI = "deepseek_ai"  # 来自 AI 估算
    BAIDU_AI = "baidu_ai"        # 来自百度热量估算
    USER_CUSTOM = "user_custom"  # 用户自定义食物
    OPENFOODFACTS = "openfoodfacts"  # 来自 Open Food Facts 数据库


class MealRecord(Base):
    """饮食记录表，记录用户每天的摄入情况"""
    __tablename__ = "meal_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    food_id = Column(Integer, nullable=True, comment="关联食物ID，若为自定义食物可为空")

    # 快照字段，记录当时的食物名称与每 100g 的营养数据
    food_name = Column(String(100), nullable=False, comment="食物名称快照")
    image_url = Column(String(500), nullable=True, comment="食物图片URL快照")
    per_100g_calories = Column(Float, nullable=False, comment="每 100g 热量（kcal）快照")
    per_100g_protein = Column(Float, nullable=False, comment="每 100g 蛋白质（g）快照")
    per_100g_fat = Column(Float, nullable=False, comment="每 100g 脂肪（g）快照")
    per_100g_carb = Column(Float, nullable=False, comment="每 100g 碳水（g）快照")

    # 实际摄入量及计算得到的营养值
    meal_date = Column(Date, nullable=False, comment="记录日期")
    meal_type = Column(SqlEnum(MealTypeEnum, values_callable=lambda x: [e.value for e in x]), nullable=False, comment="餐次类型")
    unit_weight = Column(Float, nullable=False, comment="摄入重量（克）")
    calories = Column(Float, nullable=False, comment="摄入热量（kcal）")
    protein = Column(Float, nullable=False, comment="摄入蛋白质（g）")
    fat = Column(Float, nullable=False, comment="摄入脂肪（g）")
    carb = Column(Float, nullable=False, comment="摄入碳水（g）")

    data_source = Column(SqlEnum(DataSourceEnum, values_callable=lambda x: [e.value for e in x]), nullable=False, default=DataSourceEnum.DATABASE, comment="营养数据来源")
    note = Column(Text, nullable=True, comment="用户备注")

    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 索引：常用查询 (user_id, meal_date)
    __table_args__ = (
        Index("idx_user_date", "user_id", "meal_date"),
    )

    def __repr__(self):
        return (
            f"<MealRecord(id={self.id}, user_id={self.user_id}, food_name='{self.food_name}', "
            f"date={self.meal_date}, type={self.meal_type}, weight={self.unit_weight}g)>")
