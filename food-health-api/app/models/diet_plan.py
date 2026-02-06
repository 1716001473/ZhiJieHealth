# -*- coding: utf-8 -*-
"""
推荐食谱数据库模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from app.database.connection import Base


class DietPlan(Base):
    """食谱计划表"""
    __tablename__ = "diet_plan"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment="食谱名称")
    description = Column(Text, comment="食谱简介")
    cover_image = Column(String(500), comment="封面图URL")
    
    # 基本属性
    duration_days = Column(Integer, default=7, comment="持续天数")
    target_user = Column(String(200), comment="适用人群描述")
    difficulty = Column(String(20), default="medium", comment="难度: easy/medium/hard")
    
    # 增强属性
    tags = Column(String(500), comment="标签（逗号分隔）：低卡,增肌,素食")
    source = Column(String(20), default="preset", comment="来源：preset/ai_generated/user_custom")
    author_id = Column(Integer, comment="作者ID（如果是用户自定义或AI生成归属的用户）", nullable=True)
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联
    days = relationship("DietPlanDay", back_populates="plan", cascade="all, delete-orphan", order_by="DietPlanDay.day_index")
    
    def __repr__(self):
        return f"<DietPlan(id={self.id}, name='{self.name}')>"


class DietPlanDay(Base):
    """食谱每日安排"""
    __tablename__ = "diet_plan_day"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("diet_plan.id", ondelete="CASCADE"), nullable=False)
    
    day_index = Column(Integer, nullable=False, comment="第几天 (1-21)")
    title = Column(String(100), comment="当日主题（如：排毒日）")
    
    # 目标营养（该日的汇总目标）
    total_calories = Column(Integer, comment="总热量 kcal")
    carb_ratio = Column(Integer, comment="碳水比例 %")
    protein_ratio = Column(Integer, comment="蛋白质比例 %")
    fat_ratio = Column(Integer, comment="脂肪比例 %")
    
    # 关联
    plan = relationship("DietPlan", back_populates="days")
    meals = relationship("DietPlanMeal", back_populates="day", cascade="all, delete-orphan", order_by="DietPlanMeal.sort_order")


class DietPlanMeal(Base):
    """食谱具体餐单"""
    __tablename__ = "diet_plan_meal"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    day_id = Column(Integer, ForeignKey("diet_plan_day.id", ondelete="CASCADE"), nullable=False)
    
    meal_type = Column(String(20), comment="餐次：breakfast/lunch/dinner/snack")
    sort_order = Column(Integer, default=0, comment="排序")
    
    # 推荐食物（简化版，不强制关联 Food 表，以便兼容 AI 生成的非库内食物）
    food_name = Column(String(100), nullable=False, comment="食物名称")
    amount_desc = Column(String(50), comment="份量描述（如：1个，200g）")
    calories = Column(Integer, comment="估算热量")
    
    # 替换方案 (JSON 字符串)
    # 格式示例: [{"name": "玉米", "amount": "1根", "calories": 150}]
    alternatives = Column(Text, comment="替换方案JSON")
    
    # 关联
    day = relationship("DietPlanDay", back_populates="meals")
