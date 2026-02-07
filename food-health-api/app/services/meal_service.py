# -*- coding: utf-8 -*-
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user_meal import MealRecord, MealTypeEnum, DataSourceEnum
from app.models.food import Food
from app.schemas.meal import MealRecordCreate, MealRecordUpdate, NutritionSummary, DailyNutritionReport


class MealService:
    def __init__(self, db: Session):
        self.db = db

    def _calculate_macros(self, weight: float, per_100g_vals: dict) -> dict:
        """根据重量计算具体营养素数值"""
        ratio = weight / 100.0
        return {
            "calories": per_100g_vals["calories"] * ratio,
            "protein": per_100g_vals["protein"] * ratio,
            "fat": per_100g_vals["fat"] * ratio,
            "carb": per_100g_vals["carb"] * ratio,
        }

    def create_meal_record(self, user_id: int, data: MealRecordCreate) -> MealRecord:
        """创建单条饮食记录"""
        per_100g = {}
        
        # 1. 确定营养基准数据
        if data.food_id:
            food = self.db.query(Food).filter(Food.id == data.food_id).first()
            if not food:
                # 如果找不到关联食物，尝试使用传入的自定义数据
                if data.per_100g_calories is None:
                     raise ValueError(f"Food ID {data.food_id} not found and no custom nutrition data provided")
                per_100g = {
                    "calories": data.per_100g_calories,
                    "protein": data.per_100g_protein or 0,
                    "fat": data.per_100g_fat or 0,
                    "carb": data.per_100g_carb or 0,
                }
            else:
                per_100g = {
                    "calories": food.calories,
                    "protein": food.protein,
                    "fat": food.fat,
                    "carb": food.carbohydrate,
                }
        else:
            # 纯自定义食物
            per_100g = {
                "calories": data.per_100g_calories or 0,
                "protein": data.per_100g_protein or 0,
                "fat": data.per_100g_fat or 0,
                "carb": data.per_100g_carb or 0,
            }

        # 2. 计算实际摄入
        actual = self._calculate_macros(data.unit_weight, per_100g)

        # 3. 创建记录
        record = MealRecord(
            user_id=user_id,
            food_id=data.food_id,
            food_name=data.food_name,
            image_url=data.image_url,
            meal_date=data.meal_date,
            meal_type=data.meal_type,
            unit_weight=data.unit_weight,
            note=data.note,
            data_source=data.data_source,

            # 快照
            per_100g_calories=per_100g["calories"],
            per_100g_protein=per_100g["protein"],
            per_100g_fat=per_100g["fat"],
            per_100g_carb=per_100g["carb"],

            # 计算值
            calories=actual["calories"],
            protein=actual["protein"],
            fat=actual["fat"],
            carb=actual["carb"],
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_meal_record(self, record_id: int, user_id: int, data: MealRecordUpdate) -> Optional[MealRecord]:
        """更新记录"""
        record = self.db.query(MealRecord).filter(
            MealRecord.id == record_id, 
            MealRecord.user_id == user_id
        ).first()
        
        if not record:
            return None
            
        # 如果更新了重量，需要重新计算营养
        if data.unit_weight is not None:
            per_100g = {
                "calories": record.per_100g_calories,
                "protein": record.per_100g_protein,
                "fat": record.per_100g_fat,
                "carb": record.per_100g_carb,
            }
            actual = self._calculate_macros(data.unit_weight, per_100g)
            
            record.unit_weight = data.unit_weight
            record.calories = actual["calories"]
            record.protein = actual["protein"]
            record.fat = actual["fat"]
            record.carb = actual["carb"]
            
        if data.meal_date:
            record.meal_date = data.meal_date
        if data.meal_type:
            record.meal_type = data.meal_type
        if data.note is not None:
            record.note = data.note
            
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete_meal_record(self, record_id: int, user_id: int) -> bool:
        """删除记录"""
        record = self.db.query(MealRecord).filter(
            MealRecord.id == record_id, 
            MealRecord.user_id == user_id
        ).first()
        
        if not record:
            return False
            
        self.db.delete(record)
        self.db.commit()
        return True

    def get_daily_report(self, user_id: int, query_date: date) -> DailyNutritionReport:
        """获取某日营养分析报告"""
        records = self.db.query(MealRecord).filter(
            MealRecord.user_id == user_id,
            MealRecord.meal_date == query_date
        ).all()
        
        # 汇总
        total_cal = sum(r.calories for r in records)
        total_protein = sum(r.protein for r in records)
        total_fat = sum(r.fat for r in records)
        total_carb = sum(r.carb for r in records)
        
        # 计算供能比 (1g蛋白质=4kcal, 1g脂肪=9kcal, 1g碳水=4kcal)
        # 此处分母用 total_cal
        if total_cal > 0:
            p_pct = (total_protein * 4 / total_cal) * 100
            f_pct = (total_fat * 9 / total_cal) * 100
            c_pct = (total_carb * 4 / total_cal) * 100
        else:
            p_pct = f_pct = c_pct = 0
            
        # 推荐值 (这里先给死值，后期从 UserProfile 获取)
        recommended = NutritionSummary(
            calories=2000,
            protein=75,  # 15% of 2000 => 300kcal => 75g
            fat=66,      # 30% of 2000 => 600kcal => 66g
            carb=275     # 55% of 2000 => 1100kcal => 275g
        )
        
        return DailyNutritionReport(
            date=query_date,
            total=NutritionSummary(
                calories=round(total_cal, 1),
                protein=round(total_protein, 1),
                fat=round(total_fat, 1),
                carb=round(total_carb, 1)
            ),
            recommended=recommended,
            protein_pct=round(p_pct, 1),
            fat_pct=round(f_pct, 1),
            carb_pct=round(c_pct, 1),
            records=records
        )
