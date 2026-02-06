# -*- coding: utf-8 -*-
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.schemas.meal import MealRecordUpdate


def main():
    try:
        MealRecordUpdate(unit_weight=100, meal_type="lunch")
    except Exception as exc:
        print(exc)
        sys.exit(1)

    print("meal update schema test ok")


if __name__ == "__main__":
    main()
