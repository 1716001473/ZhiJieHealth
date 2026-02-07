# -*- coding: utf-8 -*-
"""
FatSecret API 服务
用于在线搜索食物数据，作为 Open Food Facts 的补充
API 文档: https://platform.fatsecret.com/docs
"""
import re
import logging
from typing import Optional, List, Dict, Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

FATSECRET_TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
FATSECRET_API_URL = "https://platform.fatsecret.com/rest/server.api"
REQUEST_TIMEOUT = 10.0


class FatSecretService:
    """FatSecret API 服务"""

    def __init__(self):
        self.client_id = settings.fatsecret_client_id
        self.client_secret = settings.fatsecret_client_secret
        self._access_token: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    async def _get_token(self) -> Optional[str]:
        """获取 OAuth 2.0 access token"""
        if self._access_token:
            return self._access_token

        if not self.is_configured:
            return None

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.post(
                    FATSECRET_TOKEN_URL,
                    data={"grant_type": "client_credentials", "scope": "basic"},
                    auth=(self.client_id, self.client_secret),
                )
                response.raise_for_status()
                data = response.json()
                self._access_token = data["access_token"]
                return self._access_token
        except Exception as e:
            logger.error(f"FatSecret token 获取失败: {e}")
            return None

    async def search_foods(self, keyword: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """搜索食物，返回统一格式的结果列表"""
        if not self.is_configured:
            return []

        token = await self._get_token()
        if not token:
            return []

        try:
            params = {
                "method": "foods.search",
                "search_expression": keyword,
                "format": "json",
                "region": "CN",
                "language": "zh",
                "max_results": max_results,
            }

            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(
                    FATSECRET_API_URL,
                    params=params,
                    headers={"Authorization": f"Bearer {token}"},
                )
                response.raise_for_status()
                data = response.json()

            foods_data = data.get("foods", {})
            if not foods_data or "food" not in foods_data:
                return []

            foods = foods_data["food"]
            if isinstance(foods, dict):
                foods = [foods]

            return [self._parse_food(f) for f in foods if f]

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                self._access_token = None
            logger.warning(f"FatSecret API 错误: {e}")
            return []
        except Exception as e:
            logger.error(f"FatSecret 搜索失败: {e}")
            return []

    def _parse_food(self, food: Dict[str, Any]) -> Dict[str, Any]:
        """解析 FatSecret 食物数据为统一格式"""
        description = food.get("food_description", "")
        nutrition = self._parse_description(description)

        return {
            "name": food.get("food_name", ""),
            "food_id": food.get("food_id", ""),
            "brand": food.get("brand_name", ""),
            "calories": nutrition.get("calories", 0),
            "protein": nutrition.get("protein", 0),
            "fat": nutrition.get("fat", 0),
            "carbohydrate": nutrition.get("carbohydrate", 0),
            "source": "fatsecret",
        }

    def _parse_description(self, desc: str) -> Dict[str, float]:
        """解析 FatSecret 的 food_description 字符串提取营养数据"""
        result = {"calories": 0, "protein": 0, "fat": 0, "carbohydrate": 0}

        # 中文格式: "每100g - 热量: 54kcal | 脂肪: 0.10g | 碳水: 13.52g | 蛋白质: 0.00g"
        # 英文格式: "Per 100g - Calories: 54kcal | Fat: 0.10g | Carbs: 13.52g | Protein: 0.00g"
        patterns = {
            "calories": [r'[热量Calories]+:\s*([\d.]+)\s*kcal', r'([\d.]+)\s*kcal'],
            "fat": [r'[脂肪Fat]+:\s*([\d.]+)\s*g'],
            "carbohydrate": [r'[碳水Carbs]+[化合物]*:\s*([\d.]+)\s*g'],
            "protein": [r'[蛋白质Protein]+:\s*([\d.]+)\s*g'],
        }

        for key, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, desc, re.IGNORECASE)
                if match:
                    try:
                        result[key] = float(match.group(1))
                    except ValueError:
                        pass
                    break

        return result


# 全局单例
fatsecret_service = FatSecretService()
