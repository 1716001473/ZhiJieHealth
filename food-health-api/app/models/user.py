# -*- coding: utf-8 -*-
"""
用户和识别历史数据库模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime

from app.database.connection import Base


class User(Base):
    """用户表"""
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(200), nullable=False, comment="密码哈希")
    nickname = Column(String(100), comment="昵称")
    avatar_url = Column(String(500), comment="头像URL")
    
    # 健康档案（用于个性化提醒）
    # 存储为逗号分隔的字符串，如 "糖尿病,高血压"
    health_conditions = Column(Text, comment="健康状况")
    allergies = Column(Text, comment="过敏原")

    # 个性化目标与偏好
    health_goal = Column(String(50), default="maintain", comment="健康目标：lose_weight/gain_muscle/maintain")
    dietary_preferences = Column(Text, comment="饮食偏好（逗号分隔）：vegetarian,no_spicy,low_sugar")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    def get_health_conditions_list(self):
        """获取健康状况列表"""
        if not self.health_conditions:
            return []
        return [c.strip() for c in self.health_conditions.split(",") if c.strip()]
    
    def get_allergies_list(self):
        """获取过敏原列表"""
        if not self.allergies:
            return []
        return [a.strip() for a in self.allergies.split(",") if a.strip()]
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class RecognitionHistory(Base):
    """识别历史表"""
    __tablename__ = "recognition_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    
    # 识别信息
    image_url = Column(String(500), comment="原始图片地址")
    recognized_food = Column(String(100), nullable=False, comment="识别结果（菜品名称）")
    confidence = Column(Float, comment="置信度 0-1")
    alternatives = Column(Text, comment="其他候选结果 JSON")
    
    # 用户确认的参数
    selected_portion = Column(String(50), comment="用户选择的份量")
    selected_cooking = Column(String(50), comment="用户选择的烹饪方式")
    
    # 计算结果
    final_calories_min = Column(Integer, comment="估算热量下限")
    final_calories_max = Column(Integer, comment="估算热量上限")
    
    # 完整识别结果缓存（JSON格式，包含营养数据、健康建议、禁忌人群等）
    result_data = Column(Text, comment="完整识别结果JSON")
    
    # 元数据
    meal_type = Column(String(20), comment="餐次：早餐/午餐/晚餐/加餐")
    note = Column(Text, comment="用户备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def __repr__(self):
        return f"<RecognitionHistory(id={self.id}, food='{self.recognized_food}')>"
