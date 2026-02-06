# -*- coding: utf-8 -*-
"""
食谱推荐服务
"""
from datetime import datetime
from typing import Any, Iterable, Optional


def select_recommended_plan(plans: Iterable[Any]) -> Optional[Any]:
    """从候选食谱中选择最新的一条"""
    latest_plan = None
    latest_time = None

    for plan in plans:
        created_at = getattr(plan, "created_at", None)
        if created_at is None and isinstance(plan, dict):
            created_at = plan.get("created_at")
        if not isinstance(created_at, datetime):
            continue

        if latest_time is None or created_at > latest_time:
            latest_time = created_at
            latest_plan = plan

    return latest_plan
