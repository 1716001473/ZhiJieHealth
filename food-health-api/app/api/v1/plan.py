# -*- coding: utf-8 -*-
"""
食谱计划 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database.connection import get_db
from app.api.v1.user import require_login, optional_login
from app.models.diet_plan import DietPlan, DietPlanDay, DietPlanMeal
from app.models.user import User
from app.schemas.response import APIResponse
from app.services.deepseek_service import deepseek_service
from app.services.plan_recommendation import select_recommended_plan
from app.services.plan_profile import build_plan_profile_text, normalize_goal, normalize_preferences

router = APIRouter()


# --- Schemas ---

class DietPlanMealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    meal_type: str
    food_name: str
    amount_desc: Optional[str]
    calories: Optional[int]
    alternatives: Optional[str]  # JSON string

class DietPlanDayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    day_index: int
    title: Optional[str]
    total_calories: Optional[int]
    meals: List[DietPlanMealResponse]

class DietPlanListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
    cover_image: Optional[str]
    duration_days: int
    tags: Optional[str]
    source: str
    difficulty: str

class DietPlanDetailResponse(DietPlanListResponse):
    model_config = ConfigDict(from_attributes=True)
    
    days: List[DietPlanDayResponse]


class PlanGenerateProfile(BaseModel):
    weight: Optional[float] = None
    height: Optional[float] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    activity: Optional[str] = None


class PlanGenerateRequest(BaseModel):
    health_profile: Optional[PlanGenerateProfile] = None
    health_goal: Optional[str] = None
    dietary_preferences: Optional[str] = None
    disliked_tags: Optional[List[str]] = None  # 用户不喜欢的标签


# --- API ---

@router.get("/plans", response_model=APIResponse[List[DietPlanListResponse]])
async def list_plans(
    tag: Optional[str] = Query(None, description="按标签筛选"),
    source: Optional[str] = Query(None, description="按来源筛选"),
    db: Session = Depends(get_db)
):
    """获取食谱列表"""
    query = db.query(DietPlan)
    
    if tag:
        query = query.filter(DietPlan.tags.like(f"%{tag}%"))
    if source:
        query = query.filter(DietPlan.source == source)
        
    plans = query.order_by(desc(DietPlan.created_at)).all()
    
    # 转换为 Response
    data = []
    for p in plans:
        data.append(DietPlanListResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            cover_image=p.cover_image,
            duration_days=p.duration_days,
            tags=p.tags,
            source=p.source,
            difficulty=p.difficulty
        ))
        
    return APIResponse.success(data=data)


@router.get("/plans/recommended", response_model=APIResponse[Optional[DietPlanDetailResponse]])
async def get_recommended_plan(
    user_id: int = Depends(optional_login),
    db: Session = Depends(get_db)
):
    """获取最新推荐食谱（不生成）"""
    author_id = user_id if user_id else 0
    plans = db.query(DietPlan).filter(
        DietPlan.author_id == author_id,
        DietPlan.source.in_(["ai_generated", "mock_data"])
    ).order_by(desc(DietPlan.created_at)).limit(10).all()

    selected = select_recommended_plan(plans)
    if not selected:
        return APIResponse.success(data=None)

    data = _get_plan_detail_data(selected.id, db)
    return APIResponse.success(data=data)


@router.get("/plans/{plan_id}", response_model=APIResponse[DietPlanDetailResponse])
async def get_plan_detail(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """获取食谱详情"""
    return APIResponse.success(data=_get_plan_detail_data(plan_id, db))

    
class ApplyPlanRequest(BaseModel):
    day_index: int
    target_date: date

@router.post("/plans/{plan_id}/apply", response_model=APIResponse)
async def apply_plan_to_record(
    plan_id: int,
    request: ApplyPlanRequest,
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db)
):
    """应用食谱到每日记录"""
    # 1. 获取食谱及对应日
    plan_day = db.query(DietPlanDay).join(DietPlan).filter(
        DietPlan.id == plan_id,
        DietPlanDay.day_index == request.day_index
    ).first()
    
    if not plan_day:
        raise HTTPException(status_code=404, detail="食谱或对应日期不存在")
    
    # 2. 遍历餐单创建记录
    import re
    from app.models.user_meal import MealRecord, DataSourceEnum, MealTypeEnum
    
    created_count = 0
    for meal in plan_day.meals:
        # 解析重量
        weight = 100.0
        if meal.amount_desc:
            # 尝试提取 "200g" 中的 200
            match = re.search(r'(\d+)', meal.amount_desc)
            if match:
                weight = float(match.group(1))
        
        # 计算每100g热量
        per_100g_cal = (meal.calories / weight * 100) if weight > 0 and meal.calories else 0
        
        # 映射餐次
        meal_type_map = {
            "breakfast": MealTypeEnum.BREAKFAST,
            "lunch": MealTypeEnum.LUNCH,
            "dinner": MealTypeEnum.DINNER,
            "snack": MealTypeEnum.SNACK
        }
        mapped_type = meal_type_map.get(meal.meal_type, MealTypeEnum.SNACK)

        record = MealRecord(
            user_id=user_id,
            meal_date=request.target_date,
            meal_type=mapped_type,
            food_name=meal.food_name,
            unit_weight=weight,
            calories=meal.calories or 0,
            # 暂时缺失宏量营养素信息，设为0
            protein=0,
            fat=0,
            carb=0,
            per_100g_calories=per_100g_cal,
            per_100g_protein=0,
            per_100g_fat=0,
            per_100g_carb=0,
            data_source=DataSourceEnum.DEEPSEEK_AI, # 假设来源为AI推荐
            note=f"来自食谱：{plan_day.plan.name} (Day {plan_day.day_index})"
        )
        db.add(record)
        created_count += 1
    
    db.commit()
    
    return APIResponse.success(message=f"已成功应用 {created_count} 条记录")


@router.post("/plans/generate", response_model=APIResponse[DietPlanDetailResponse])
async def generate_plan(
    force_new: bool = False,
    payload: Optional[PlanGenerateRequest] = None,
    user_id: int = Depends(optional_login),
    db: Session = Depends(get_db)
):
    """
    [AI] 生成个性化食谱
    :param force_new: 是否强制重新生成（忽略今日缓存）
    """
    # 1. 检查今日已生成食谱 (除非强制生成)
    existing_plan = None
    if not force_new and user_id:  # 只在用户已登录时检查缓存
        today_start = datetime.combine(date.today(), time.min)
        existing_plan = db.query(DietPlan).filter(
            DietPlan.author_id == user_id,
            DietPlan.source == "ai_generated",
            DietPlan.created_at >= today_start
        ).order_by(desc(DietPlan.created_at)).first()
    
    if existing_plan:
        data = _get_plan_detail_data(existing_plan.id, db)
        return APIResponse.success(data=data)

    # 2. 准备用户信息
    payload_goal = payload.health_goal if payload else None
    payload_prefs = payload.dietary_preferences if payload else None
    payload_profile = payload.health_profile.model_dump() if payload and payload.health_profile else {}
    payload_disliked = payload.disliked_tags if payload and payload.disliked_tags else []

    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            goal = payload_goal or user.health_goal or "keep_fit"
            prefs = payload_prefs or user.dietary_preferences or "无特殊偏好"
        else:
            # Token valid but user not found
            goal = payload_goal or "keep_fit"
            prefs = payload_prefs or "无特殊偏好"
    else:
        # 使用默认用户配置（未登录时）
        goal = payload_goal or "keep_fit"  # 默认维持健康
        prefs = payload_prefs or "无特殊偏好"

    goal_key, goal_label = normalize_goal(goal)
    prefs_label = normalize_preferences(prefs)

    if user_id and user:
        nickname = user.nickname or user.username
    else:
        nickname = None

    user_profile = build_plan_profile_text(
        nickname=nickname,
        health_goal=goal_key,
        dietary_preferences=prefs,
        health_profile=payload_profile
    )

    # 3. 尝试调用 AI 生成（传递不喜欢的标签）
    try:
        plan_data = await deepseek_service.generate_diet_plan(
            user_profile,
            goal_label,
            prefs_label,
            disliked_tags=payload_disliked  # 传递用户不喜欢的标签
        )
    except Exception as e:
        print(f"⚠️ 调用 AI 服务异常: {e}")
        plan_data = None
    
    new_plan = None
    
    if plan_data:
        # === AI 路径 ===
        try:
            # 提取并组合标签
            ai_tags = plan_data.get("tags", [])
            # 确保 ai_tags 里面的每一项都是 string
            ai_tags = [str(t) for t in ai_tags]
            
            # 3.1 基础标签映射 (Goal -> Tag)
            goal_map = {
                "lose_weight": "减脂",
                "loss_weight": "减脂",
                "keep_fit": "维持",
                "maintain": "维持",
                "gain_muscle": "增肌",
                "减脂": "减脂",
                "增肌": "增肌",
                "保持健康": "维持",
                "维持": "维持"
            }
            mapped_goal_tag = goal_map.get(goal_key, goal_label)
            
            base_tags = ["DeepSeek", "AI定制", mapped_goal_tag]
            
            # 3.2 强制素食标签检测 (Prefs/Name -> Tag)
            # 如果偏好含素，或标题含素，强制打上"素食"标签
            if "素" in prefs or "素" in plan_data.get("name", ""):
                 base_tags.append("素食")

            # 去重合并
            final_tags = list(set(base_tags + ai_tags))
            tags_str = ",".join(final_tags)

            new_plan = DietPlan(
                name=plan_data.get("name", f"AI定制：{goal_label}食谱"),
                description=plan_data.get("description", "为您量身定制的7天健康饮食计划"),
                cover_image="/static/ai_plan.png",
                duration_days=7,
                tags=tags_str,
                source="ai_generated",
                difficulty="medium",
                target_user=f"{user_profile} | {goal_label}",
                author_id=user_id if user_id else 0  # 未登录时使用 0
            )
            db.add(new_plan)
            db.commit()
            db.refresh(new_plan)
            
            # 处理每一天
            for day_info in plan_data.get("days", []):
                day = DietPlanDay(
                    plan_id=new_plan.id,
                    day_index=day_info.get("day_index"),
                    title=day_info.get("title", f"Day {day_info.get('day_index')}"),
                    total_calories=0 # AI 可能未直接返回总热量，需累加
                )
                db.add(day)
                db.commit()
                db.refresh(day)
                
                day_total_cal = 0
                
                # 处理每一餐
                meals_list = day_info.get("meals", [])
                for idx, meal_info in enumerate(meals_list):
                    # 安全转换热量
                    raw_cal = meal_info.get("calories", 0)
                    safe_cal = 0
                    try:
                        # 尝试去除非数字字符
                        if isinstance(raw_cal, str):
                            import re
                            # 提取第一个数字序列
                            match = re.search(r'\d+', raw_cal)
                            if match:
                                safe_cal = int(match.group())
                        else:
                            safe_cal = int(raw_cal)
                    except (ValueError, TypeError):
                        safe_cal = 0
                        
                    day_total_cal += safe_cal
                    
                    meal_obj = DietPlanMeal(
                        day_id=day.id,
                        meal_type=meal_info.get("meal_type", "snack"),
                        sort_order=idx + 1,
                        # Truncate to match DB constraints
                        food_name=str(meal_info.get("food_name", "未命名食物"))[:100],
                        amount_desc=str(meal_info.get("amount_desc", ""))[:50],
                        calories=safe_cal
                    )
                    db.add(meal_obj)
                
                # 更新每日总热量
                day.total_calories = day_total_cal
                db.add(day)
            
            db.commit()
            print(f"✅ AI 食谱已保存: Plan ID {new_plan.id}")

        except Exception as e:
            print(f"❌ 保存 AI 食谱失败，回退到 Mock: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            new_plan = None  # 触发下面的 fallback
            
    if not new_plan:
        # === Fallback Mock 路径 ===
        print("⚠️ 启用 Mock 数据生成")
        new_plan = DietPlan(
            name=f"推荐食谱：{goal_label}计划 (Mock)",
            description=f"AI 服务暂时繁忙，为您生成的推荐计划。目标：{goal_label}",
            cover_image="/static/mock_plan.png",
            duration_days=7,
            tags="Mock,示例,推荐",
            source="mock_data",
            difficulty="easy",
            target_user=user_profile,
            author_id=user_id if user_id else 0  # 未登录时使用 0
        )
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)

        # 只生成第一天作为示例
        day1 = DietPlanDay(
            plan_id=new_plan.id, 
            day_index=1, 
            title="启动日 (示例)", 
            total_calories=1500
        )
        db.add(day1)
        db.commit()
        db.refresh(day1)

        meals_data = [
            {"type": "breakfast", "name": "全麦面包+牛奶", "amount": "2片+1杯", "cal": 350},
            {"type": "lunch", "name": "鸡胸肉蔬菜沙拉", "amount": "1份", "cal": 450},
            {"type": "dinner", "name": "清蒸鲈鱼+杂粮饭", "amount": "100g+1碗", "cal": 400},
            {"type": "snack", "name": "苹果", "amount": "1个", "cal": 80}
        ]
        
        for idx, m in enumerate(meals_data):
            meal = DietPlanMeal(
                day_id=day1.id,
                meal_type=m["type"],
                sort_order=idx,
                food_name=m["name"],
                amount_desc=m["amount"],
                calories=m["cal"]
            )
            db.add(meal)
        db.commit()
    
    # 4. 返回结果
    data = _get_plan_detail_data(new_plan.id, db)
    return APIResponse.success(data=data)


def _get_plan_detail_data(plan_id: int, db: Session) -> DietPlanDetailResponse:
    """Helper to build plan detail response"""
    plan = db.query(DietPlan).filter(DietPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="食谱不存在")
        
    days_data = []
    # Ensure days are sorted
    sorted_days = sorted(plan.days, key=lambda x: x.day_index)
    
    for day in sorted_days:
        meals_data = []
        # Ensure meals are sorted
        sorted_meals = sorted(day.meals, key=lambda x: x.sort_order)
        
        for meal in sorted_meals:
            meals_data.append(DietPlanMealResponse(
                meal_type=meal.meal_type,
                food_name=meal.food_name,
                amount_desc=meal.amount_desc,
                calories=meal.calories,
                alternatives=meal.alternatives
            ))
        
        days_data.append(DietPlanDayResponse(
            day_index=day.day_index,
            title=day.title,
            total_calories=day.total_calories,
            meals=meals_data
        ))
    
    return DietPlanDetailResponse(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        cover_image=plan.cover_image,
        duration_days=plan.duration_days,
        tags=plan.tags,
        source=plan.source,
        difficulty=plan.difficulty,
        days=days_data
    )

