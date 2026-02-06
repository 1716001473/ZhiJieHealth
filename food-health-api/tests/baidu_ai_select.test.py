# -*- coding: utf-8 -*-
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from app.services.baidu_ai import BaiduAIService
from app.schemas.recognition import RecognitionResult


async def fake_request(self, url, image_base64, top_num, category_label, extra_data=None):
    if "dish" in url:
        return [
            RecognitionResult(name="韭菜", confidence=0.21, category=category_label),
        ]
    if "fruit" in url:
        return [
            RecognitionResult(name="番茄", confidence=0.96, category=category_label),
        ]
    return [
        RecognitionResult(name="茄科植物", confidence=0.33, category=category_label),
    ]


def main():
    service = BaiduAIService()
    service.api_key = "test-key"
    service.secret_key = "test-secret"
    service.access_token = "token"

    service._request_recognition = fake_request.__get__(service, BaiduAIService)

    results = asyncio.run(service._recognize_with_fallback("base64", 5))
    if not results or results[0].name != "番茄":
        print("baidu ai select test failed")
        sys.exit(1)

    print("baidu ai select test ok")


if __name__ == "__main__":
    main()
