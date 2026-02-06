# -*- coding: utf-8 -*-
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.services.plan_recommendation import select_recommended_plan


def main():
    now = datetime(2026, 2, 3, 10, 0, 0)
    plans = [
        {"id": 1, "created_at": now - timedelta(days=2)},
        {"id": 2, "created_at": now},
        {"id": 3, "created_at": now - timedelta(days=1)}
    ]

    selected = select_recommended_plan(plans)
    assert selected["id"] == 2

    assert select_recommended_plan([]) is None

    print('plan recommendation test ok')


if __name__ == '__main__':
    main()
