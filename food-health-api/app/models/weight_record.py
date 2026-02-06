# -*- coding: utf-8 -*-
"""
体重记录模型
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, Float, Date, DateTime, Index
from app.database.connection import Base

class WeightRecord(Base):
    """用户体重历史记录"""
    __tablename__ = "weight_record"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, comment="用户ID")
    weight = Column(Float, nullable=False, comment="体重(kg)")
    record_date = Column(Date, default=date.today, comment="记录日期")
    
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 索引
    __table_args__ = (
        Index("idx_weight_user_date", "user_id", "record_date"),
    )

    def __repr__(self):
        return f"<WeightRecord(user_id={self.user_id}, date={self.record_date}, weight={self.weight})>"
