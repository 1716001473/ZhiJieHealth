# -*- coding: utf-8 -*-
"""
AI 食谱生成服务
调用豆包文本模型批量生成精品食谱数据
"""
import json
import re
import logging
from typing import List, Dict, Any, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# 9 个分类及每类生成数量
CATEGORIES = {
    "早餐": {"count": 4, "desc": "适合早晨食用的营养早餐，简单快手"},
    "午餐": {"count": 5, "desc": "丰富的午间正餐，营养均衡"},
    "晚餐": {"count": 5, "desc": "清淡健康的晚餐，易消化"},
    "汤羹": {"count": 4, "desc": "各类营养汤品和羹类"},
    "凉菜": {"count": 3, "desc": "清爽开胃的凉拌菜"},
    "烘焙": {"count": 3, "desc": "健康低糖烘焙食品"},
    "轻食": {"count": 4, "desc": "低卡轻食沙拉，适合减脂"},
    "控糖": {"count": 4, "desc": "适合控制血糖的低GI菜品"},
    "增肌": {"count": 4, "desc": "高蛋白增肌餐，适合健身人群"},
}


class RecipeGenerator:
    """AI 食谱生成器"""

    def __init__(self):
        self.api_key = settings.doubao_api_key
        self.base_url = settings.doubao_base_url or "https://ark.cn-beijing.volces.com/api/v3"
        self.model = settings.doubao_model

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key and self.model)

    async def generate_recipes_for_category(
        self, category: str, count: int, existing_names: List[str]
    ) -> List[Dict[str, Any]]:
        """为指定分类生成食谱"""
        if not self.is_configured:
            logger.error("豆包AI未配置，无法生成食谱")
            return []

        prompt = self._build_prompt(category, count, existing_names)
        text = await self._call_text_api(prompt)
        if not text:
            return []

        recipes = self._parse_recipes(text, category)
        return recipes

    def _build_prompt(self, category: str, count: int, existing_names: List[str]) -> str:
        """构建食谱生成 prompt"""
        existing_str = "、".join(existing_names[-20:]) if existing_names else "无"
        cat_desc = CATEGORIES.get(category, {}).get("desc", "")

        return f"""你是一位专业的中式营养师和厨师。请为"{category}"分类生成{count}道精品食谱。
分类说明：{cat_desc}

要求：
1. 菜品名称不能与以下已有菜品重复：{existing_str}
2. 每道菜可以有多个标签（从以下选择：早餐、午餐、晚餐、汤羹、凉菜、烘焙、轻食、控糖、增肌），主分类"{category}"必须包含在标签中
3. 营养数据必须合理准确（基于每份的实际营养成分）
4. 食材用量要具体（如"200g"、"2个"、"1勺"）
5. 步骤要详细实用，每道菜4-6个步骤
6. 菜品要有中国特色，贴近日常生活

请严格按照以下JSON数组格式返回，不要有任何其他文字说明：
[
  {{
    "name": "菜品名称",
    "description": "一句话描述（30字以内）",
    "category": "{category}",
    "tags": ["{category}", "其他标签"],
    "cook_time": "15分钟",
    "prep_time": "10分钟",
    "servings": 2,
    "difficulty": "简单",
    "calories": 350,
    "protein": 25.0,
    "fat": 12.0,
    "carbs": 30.0,
    "fiber": 3.0,
    "sodium": 450,
    "ingredients": [
      {{"name": "食材名", "amount": "用量"}}
    ],
    "steps": [
      {{"step": 1, "content": "步骤说明"}}
    ],
    "tips": "烹饪小贴士",
    "suitable_for": "适合人群描述",
    "not_suitable_for": "不适合人群描述"
  }}
]"""

    async def _call_text_api(self, prompt: str) -> Optional[str]:
        """调用豆包文本 API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业的中式营养师和厨师，擅长设计健康食谱。请严格按照用户要求的JSON格式返回数据。"},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 4096,
            "temperature": 0.7,
        }

        api_url = f"{self.base_url}/chat/completions"
        logger.info(f"调用豆包文本API: {api_url}, 模型: {self.model}")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(api_url, headers=headers, json=payload)

                if response.status_code != 200:
                    logger.error(f"豆包API错误: {response.status_code} - {response.text[:500]}")
                    return None

                result = response.json()
                choices = result.get("choices", [])
                if not choices:
                    logger.warning("豆包返回的 choices 为空")
                    return None

                text = choices[0].get("message", {}).get("content", "")
                logger.info(f"豆包返回文本长度: {len(text)}")
                return text

        except Exception as e:
            logger.error(f"调用豆包API失败: {type(e).__name__}: {e}")
            return None

    def _parse_recipes(self, text: str, category: str) -> List[Dict[str, Any]]:
        """解析 AI 返回的食谱 JSON"""
        json_data = self._extract_json_array(text)
        if not json_data:
            logger.warning(f"无法从返回文本中提取JSON数组")
            return []

        recipes = []
        for item in json_data:
            try:
                recipe = {
                    "name": item.get("name", ""),
                    "description": item.get("description", ""),
                    "category": item.get("category", category),
                    "tags": item.get("tags", [category]),
                    "cook_time": item.get("cook_time", ""),
                    "prep_time": item.get("prep_time", ""),
                    "servings": item.get("servings", 2),
                    "difficulty": item.get("difficulty", "简单"),
                    "calories": item.get("calories", 0),
                    "protein": item.get("protein", 0.0),
                    "fat": item.get("fat", 0.0),
                    "carbs": item.get("carbs", 0.0),
                    "fiber": item.get("fiber", 0.0),
                    "sodium": item.get("sodium", 0),
                    "ingredients": item.get("ingredients", []),
                    "steps": item.get("steps", []),
                    "tips": item.get("tips", ""),
                    "suitable_for": item.get("suitable_for", ""),
                    "not_suitable_for": item.get("not_suitable_for", ""),
                    "is_featured": True,
                    "is_active": True,
                }
                if recipe["name"]:
                    recipes.append(recipe)
            except Exception as e:
                logger.warning(f"解析单条食谱失败: {e}")
                continue

        logger.info(f"成功解析 {len(recipes)} 条食谱")
        return recipes

    def _extract_json_array(self, text: str) -> Optional[List]:
        """从文本中提取 JSON 数组"""
        # 直接解析
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        # 提取 ```json ... ``` 代码块
        match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
        if match:
            try:
                data = json.loads(match.group(1))
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass

        # 提取 [ ... ] 部分
        bracket_match = re.search(r'\[[\s\S]*\]', text)
        if bracket_match:
            try:
                data = json.loads(bracket_match.group(0))
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass

        return None
