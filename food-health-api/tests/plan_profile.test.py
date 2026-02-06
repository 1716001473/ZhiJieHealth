# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.services.plan_profile import build_plan_profile_text, normalize_goal, normalize_preferences


def main():
    goal_key, goal_label = normalize_goal('maintain')
    assert goal_key == 'maintain'
    assert goal_label == '保持健康'

    prefs = normalize_preferences('vegetarian,low_sugar')
    assert '素食' in prefs
    assert '低糖' in prefs

    profile = {
        'weight': 68,
        'height': 174,
        'age': 22,
        'gender': 'male',
        'activity': 'medium'
    }

    text = build_plan_profile_text(
        nickname='阿明',
        health_goal='maintain',
        dietary_preferences='vegetarian,low_sugar',
        health_profile=profile
    )

    assert '阿明' in text
    assert '68kg' in text
    assert '174cm' in text
    assert '22岁' in text
    assert '男' in text
    assert '中等' in text
    assert '保持健康' in text
    assert '素食' in text
    assert '低糖' in text

    print('plan profile test ok')


if __name__ == '__main__':
    main()
