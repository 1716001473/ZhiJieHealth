# -*- coding: utf-8 -*-
"""
Open Food Facts API 服务
按需从 Open Food Facts 获取食物数据并缓存到本地
"""
import httpx
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Open Food Facts API 配置
OFF_API_BASE = "https://world.openfoodfacts.org"
OFF_SEARCH_URL = f"{OFF_API_BASE}/cgi/search.pl"
OFF_PRODUCT_URL = f"{OFF_API_BASE}/api/v2/product"

# 请求超时设置
REQUEST_TIMEOUT = 10.0


class OpenFoodFactsService:
    """Open Food Facts API 服务"""

    def __init__(self):
        self.headers = {
            "User-Agent": "FoodHealthApp/1.0 (https://github.com/food-health-app)"
        }

    async def search_foods(self, keyword: str, page_size: int = 10) -> List[Dict[str, Any]]:
        """
        搜索食物

        Args:
            keyword: 搜索关键词
            page_size: 返回数量

        Returns:
            食物列表
        """
        try:
            params = {
                "search_terms": keyword,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": page_size,
                "fields": "code,product_name,product_name_zh,brands,nutriments,image_url,categories_tags",
            }

            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(
                    OFF_SEARCH_URL,
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()

            products = data.get("products", [])
            return [self._parse_product(p) for p in products if self._is_valid_product(p)]

        except httpx.TimeoutException:
            logger.warning(f"Open Food Facts API 超时: {keyword}")
            return []
        except Exception as e:
            logger.error(f"Open Food Facts API 错误: {e}")
            return []

    async def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        根据条形码获取产品

        Args:
            barcode: 产品条形码

        Returns:
            产品信息
        """
        try:
            url = f"{OFF_PRODUCT_URL}/{barcode}.json"
            params = {
                "fields": "code,product_name,product_name_zh,brands,nutriments,image_url,categories_tags"
            }

            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()

            if data.get("status") == 1:
                product = data.get("product", {})
                if self._is_valid_product(product):
                    return self._parse_product(product)

            return None

        except Exception as e:
            logger.error(f"获取产品失败 [{barcode}]: {e}")
            return None

    def _is_valid_product(self, product: Dict[str, Any]) -> bool:
        """检查产品数据是否有效"""
        # 必须有名称
        name = product.get("product_name_zh") or product.get("product_name")
        if not name:
            return False

        # 必须有营养数据
        nutriments = product.get("nutriments", {})
        if not nutriments:
            return False

        # 至少有热量数据
        calories = nutriments.get("energy-kcal_100g") or nutriments.get("energy_100g")
        if calories is None:
            return False

        return True

    def _parse_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析产品数据为统一格式

        Args:
            product: Open Food Facts 原始产品数据

        Returns:
            统一格式的产品数据
        """
        nutriments = product.get("nutriments", {})

        # 优先使用中文名称
        name = product.get("product_name_zh") or product.get("product_name", "")

        # 品牌信息
        brands = product.get("brands", "")
        if brands and brands not in name:
            display_name = f"{brands} {name}".strip()
        else:
            display_name = name

        # 安全转换数值的辅助函数
        def safe_float(value, default=0.0) -> float:
            if value is None:
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        # 热量处理 (Open Food Facts 可能用 kJ 或 kcal)
        calories = safe_float(nutriments.get("energy-kcal_100g"))
        if calories == 0:
            # 如果只有 kJ，转换为 kcal (1 kcal ≈ 4.184 kJ)
            energy_kj = safe_float(nutriments.get("energy_100g")) or safe_float(nutriments.get("energy-kj_100g"))
            if energy_kj:
                calories = energy_kj / 4.184

        return {
            "barcode": product.get("code", ""),
            "name": display_name[:100],  # 限制长度
            "original_name": product.get("product_name", ""),
            "brands": brands,
            "calories": round(calories, 1),
            "protein": round(safe_float(nutriments.get("proteins_100g")), 1),
            "fat": round(safe_float(nutriments.get("fat_100g")), 1),
            "carbohydrate": round(safe_float(nutriments.get("carbohydrates_100g")), 1),
            "fiber": round(safe_float(nutriments.get("fiber_100g")), 1),
            "sodium": round(safe_float(nutriments.get("sodium_100g")) * 1000, 1),  # g -> mg
            "sugar": round(safe_float(nutriments.get("sugars_100g")), 1),
            "image_url": product.get("image_url", ""),
            "categories": product.get("categories_tags", []),
            "source": "openfoodfacts",
        }


# 单例实例
off_service = OpenFoodFactsService()
