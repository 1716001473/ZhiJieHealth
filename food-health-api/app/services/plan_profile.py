# -*- coding: utf-8 -*-
"""
食谱用户画像构建
"""
from typing import Any, Dict, Optional, Tuple


GOAL_LABELS = {
    "lose_weight": "减脂",
    "loss_weight": "减脂",
    "keep_fit": "保持健康",
    "maintain": "保持健康",
    "gain_muscle": "增肌增重"
}

PREFERENCE_LABELS = {
    "vegetarian": "素食",
    "no_spicy": "不吃辣",
    "low_sugar": "低糖",
    "high_protein": "高蛋白",
    "lactose_free": "乳糖不耐受"
}

GENDER_LABELS = {
    "male": "男",
    "female": "女"
}

ACTIVITY_LABELS = {
    "low": "轻量",
    "medium": "中等",
    "high": "高强度"
}


def normalize_goal(goal: Optional[str]) -> Tuple[str, str]:
    if not goal:
        return "keep_fit", "保持健康"
    normalized = str(goal).strip()
    label = GOAL_LABELS.get(normalized, normalized)
    return normalized, label


def normalize_preferences(preferences: Any) -> str:
    if not preferences:
        return "无特殊偏好"

    if isinstance(preferences, str):
        raw_items = [item.strip() for item in preferences.split(",") if item.strip()]
    elif isinstance(preferences, (list, tuple, set)):
        raw_items = [str(item).strip() for item in preferences if str(item).strip()]
    else:
        raw_items = [str(preferences).strip()] if str(preferences).strip() else []

    labels = []
    for item in raw_items:
        labels.append(PREFERENCE_LABELS.get(item, item))

    return "、".join(labels) if labels else "无特殊偏好"


def _format_number(value: Any, digits: int = 1) -> Optional[str]:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number.is_integer():
        return str(int(number))
    return f"{number:.{digits}f}"


def build_plan_profile_text(
    nickname: Optional[str],
    health_goal: Optional[str],
    dietary_preferences: Optional[str],
    health_profile: Optional[Dict[str, Any]]
) -> str:
    goal_key, goal_label = normalize_goal(health_goal)
    prefs_label = normalize_preferences(dietary_preferences)

    name = nickname or "默认用户"
    parts = [name]

    if health_profile:
        weight = _format_number(health_profile.get("weight"))
        height = _format_number(health_profile.get("height"))
        age = _format_number(health_profile.get("age"), digits=0)
        gender = GENDER_LABELS.get(health_profile.get("gender"), "")
        activity = ACTIVITY_LABELS.get(health_profile.get("activity"), "")

        if gender:
            parts.append(f"性别：{gender}")
        if age:
            parts.append(f"年龄：{age}岁")
        if height:
            parts.append(f"身高：{height}cm")
        if weight:
            parts.append(f"体重：{weight}kg")
        if activity:
            parts.append(f"活动水平：{activity}")

    parts.append(f"目标：{goal_label}")
    parts.append(f"偏好：{prefs_label}")

    return "，".join(parts)
