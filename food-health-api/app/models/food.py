# -*- coding: utf-8 -*-
"""
食物相关数据库模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class Food(Base):
    """食物/菜品表"""
    __tablename__ = "food"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, comment="菜品名称")
    alias = Column(String(200), comment="别名，逗号分隔")
    category = Column(String(50), comment="分类：主食/荤菜/素菜/汤类/饮品/水果/零食")
    
    # 营养数据（每100g）
    calories = Column(Float, comment="热量 kcal")
    protein = Column(Float, comment="蛋白质 g")
    fat = Column(Float, comment="脂肪 g")
    carbohydrate = Column(Float, comment="碳水化合物 g")
    fiber = Column(Float, comment="膳食纤维 g")
    sodium = Column(Float, comment="钠 mg")
    sugar = Column(Float, comment="糖 g")
    
    # 份量参考
    serving_desc = Column(String(100), comment="常规份量描述")
    serving_weight = Column(Integer, default=100, comment="常规份量重量 g")
    
    # 健康评级
    health_rating = Column(String(20), default="适量", comment="健康评级：推荐/适量/少食")
    health_tips = Column(Text, comment="健康提示/食用建议")
    
    # 元数据
    image_url = Column(String(500), comment="示例图片URL")
    source = Column(String(100), comment="数据来源")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    # 关联
    contraindications = relationship("FoodContraindication", back_populates="food", cascade="all, delete-orphan")
    portions = relationship("FoodPortion", back_populates="food", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Food(id={self.id}, name='{self.name}')>"


class FoodTemp(Base):
    """临时食物表（AI/用户补充的待校验数据）"""
    __tablename__ = "food_temp"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, comment="食物名称")

    calories = Column(Float, nullable=False, comment="热量 kcal/100g")
    protein = Column(Float, nullable=False, comment="蛋白质 g/100g")
    fat = Column(Float, nullable=False, comment="脂肪 g/100g")
    carbohydrate = Column(Float, nullable=False, comment="碳水化合物 g/100g")

    source = Column(String(50), comment="数据来源")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    def __repr__(self):
        return f"<FoodTemp(id={self.id}, name='{self.name}', source='{self.source}')>"


class FoodContraindication(Base):
    """禁忌规则表（不适宜人群）"""
    __tablename__ = "food_contraindication"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    food_id = Column(Integer, ForeignKey("food.id", ondelete="CASCADE"), nullable=True, comment="关联食物ID")
    food_keyword = Column(String(100), comment="食物关键词，用于模糊匹配")
    
    condition_type = Column(String(50), nullable=False, comment="疾病/人群类型")
    # 可选值：糖尿病/高血压/痛风/高血脂/肾病/孕妇/哺乳期/婴幼儿/过敏体质/胃病
    
    severity = Column(String(20), nullable=False, default="慎食", comment="严重程度：禁食/慎食/少食")
    reason = Column(Text, comment="原因说明")
    suggestion = Column(Text, comment="替代建议")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联
    food = relationship("Food", back_populates="contraindications")
    
    def __repr__(self):
        return f"<FoodContraindication(id={self.id}, condition='{self.condition_type}')>"


class FoodPortion(Base):
    """食物份量选项表"""
    __tablename__ = "food_portion"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    food_id = Column(Integer, ForeignKey("food.id", ondelete="CASCADE"), nullable=True, comment="关联食物ID")
    category = Column(String(50), comment="或关联分类")
    
    portion_name = Column(String(50), nullable=False, comment="份量名称：小份/中份/大份")
    weight_grams = Column(Integer, comment="对应重量 g")
    calorie_factor = Column(Float, default=1.0, comment="热量系数")
    
    is_default = Column(Boolean, default=False, comment="是否默认选项")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    
    # 关联
    food = relationship("Food", back_populates="portions")
    
    def __repr__(self):
        return f"<FoodPortion(id={self.id}, name='{self.portion_name}')>"


class CookingMethod(Base):
    """烹饪方式表"""
    __tablename__ = "cooking_method"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, comment="烹饪方式名称")
    calorie_adjust = Column(Integer, default=0, comment="热量调整值 kcal")
    calorie_percent = Column(Float, default=0, comment="热量调整百分比")
    description = Column(String(200), comment="说明")
    icon = Column(String(50), comment="图标名称")
    sort_order = Column(Integer, default=0, comment="排序顺序")
    
    def __repr__(self):
        return f"<CookingMethod(id={self.id}, name='{self.name}')>"
