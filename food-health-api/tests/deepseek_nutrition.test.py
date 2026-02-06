# -*- coding: utf-8 -*-
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from app.services.deepseek_service import DeepSeekService
import app.services.deepseek_service as deepseek_module


class FakeResponse:
    status_code = 200

    def json(self):
        return {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "calories": 18,
                            "protein": 0.9,
                            "fat": 0.2,
                            "carbohydrate": 3.9,
                            "gi": 30,
                            "health_rating": "推荐",
                            "health_tips": "富含维生素，适量即可",
                            "contraindications": [],
                        })
                    }
                }
            ]
        }


class FakeClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        return FakeResponse()


def main():
    deepseek_module.httpx.AsyncClient = FakeClient

    service = DeepSeekService()
    service.api_key = "test-key"
    service.base_url = "http://test-host"

    result = asyncio.run(service.get_nutrition_info("番茄"))
    if not result or result.get("calories") != 18:
        print("deepseek nutrition test failed")
        sys.exit(1)

    print("deepseek nutrition test ok")


if __name__ == "__main__":
    main()
