# -*- coding: utf-8 -*-
"""
豆包 AI 视觉理解服务（火山引擎方舟）
用于食物识别和热量估算

使用 OpenAI 兼容格式 API (/chat/completions)
"""
import base64
import json
import re
import logging
from typing import List, Optional, Dict, Any

import httpx

from app.config import get_settings
from app.schemas.recognition import RecognitionResult

logger = logging.getLogger(__name__)
settings = get_settings()


class DoubaoAIService:
    """豆包 AI 视觉理解服务"""
    
    def __init__(self):
        self.api_key = settings.doubao_api_key
        self.base_url = settings.doubao_base_url or "https://ark.cn-beijing.volces.com/api/v3"
        self.model = settings.doubao_model
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置豆包AI"""
        return bool(self.api_key and self.model)
    
    async def recognize_food(self, image_base64: str) -> List[RecognitionResult]:
        """
        识别食物并估算热量
        
        Args:
            image_base64: 图片的 base64 编码
            
        Returns:
            识别结果列表
        """
        if not self.is_configured:
            logger.warning("⚠️ 豆包AI未配置，使用模拟数据")
            return self._get_mock_results()
        
        try:
            # 构建请求
            result = await self._call_vision_api(image_base64)
            
            if result:
                return [result]
            else:
                logger.warning("⚠️ 豆包AI未能识别食物")
                return []
                
        except Exception as e:
            logger.error(f"❌ 豆包AI调用失败: {type(e).__name__}: {str(e)}")
            raise
    
    async def _call_vision_api(self, image_base64: str) -> Optional[RecognitionResult]:
        """
        调用豆包视觉理解 API
        
        使用 OpenAI 兼容格式的 /chat/completions API
        """
        # 构建 data URL
        image_url = f"data:image/jpeg;base64,{image_base64}"
        
        # 构建 prompt，引导模型返回结构化数据
        prompt = """请识别图片中的食物，并提供以下信息。请严格按照 JSON 格式返回，不要有其他文字：

{
  "name": "食物名称（生食材用原名如'茼蒿'、'鸡胸肉'；熟菜品用菜名如'清炒茼蒿'、'番茄炒蛋'）",
  "food_state": "raw 或 cooked（raw=未烹饪的生鲜食材，cooked=已烹饪的成品菜）",
  "confidence": 0.95,
  "category": "分类（生鲜蔬菜、生鲜肉类、生鲜水产、水果、荤菜、素菜、主食、汤类、饮品、零食）",
  "cooking_method": "烹饪方式（生食材填null，熟菜品填具体方式如油焖、清蒸、凉拌）",
  "estimated_weight_grams": 300,
  "calories_per_100g": 150,
  "total_calories_min": 350,
  "total_calories_max": 450,
  "nutrition": {
    "protein": 25.0,
    "fat": 12.0,
    "carbohydrate": 30.0,
    "fiber": 2.0,
    "sodium": 500
  },
  "health_tips": "简短的健康建议（1-2句话）",
  "analysis": "简短的分析说明",
  "contraindications": [
    {
      "condition": "高血脂",
      "severity": "少食",
      "reason": "脂肪含量较高",
      "advice": "建议适量食用，搭配蔬菜"
    }
  ]
}

注意：
1. 首先判断图片中的食物是生鲜食材还是已烹饪的菜品
2. 如果是未烹饪的生鲜食材（如生蔬菜、生肉、整个水果等），food_state 设为 "raw"，name 用食材原名（如"茼蒿"而非"清炒茼蒿"），cooking_method 设为 null，营养数据基于生食材每100g的数值
3. 如果是已烹饪的成品菜，food_state 设为 "cooked"，name 用菜品全名，营养数据要考虑烹饪方式（油炸热量高，清蒸热量低）
4. 如果图片中有多个食物，只识别主要的一个
5. 给出热量范围而不是精确值
6. contraindications 必须返回，根据食物特性判断不适宜人群（如高血脂、糖尿病、高血压、痛风、肾病等），severity 可以是"禁食"、"少食"或"适量\""""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        # 使用 OpenAI 兼容格式
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
            "max_tokens": 1024,
            "thinking": {"type": "disabled"},
        }
        
        api_url = f"{self.base_url}/chat/completions"
        
        logger.info(f"🔍 调用豆包AI视觉识别 API...")
        logger.info(f"   端点: {api_url}")
        logger.info(f"   模型: {self.model}")
        logger.info(f"   图片大小: {len(image_base64)} 字符")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                api_url,
                headers=headers,
                json=payload,
            )
            
            if response.status_code != 200:
                error_text = response.text[:500] if response.text else "无响应内容"
                logger.error(f"❌ 豆包API返回错误: {response.status_code} - {error_text}")
                raise ValueError(f"豆包API错误: {response.status_code} - {error_text}")
            
            result = response.json()
            logger.info(f"📥 豆包AI返回成功")
        
        # 解析返回结果
        return self._parse_response(result)
    
    def _parse_response(self, response: Dict[str, Any]) -> Optional[RecognitionResult]:
        """
        解析豆包 API 返回的响应（OpenAI 兼容格式）
        
        返回格式：
        {
            "id": "...",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "...JSON内容..."
                    }
                }
            ],
            ...
        }
        """
        try:
            # 提取文本内容
            choices = response.get("choices", [])
            if not choices:
                logger.warning("⚠️ 豆包返回的 choices 为空")
                return None
            
            message = choices[0].get("message", {})
            text = message.get("content", "")
            
            if not text:
                logger.warning("⚠️ 豆包返回的 content 为空")
                return None
            
            logger.info(f"📝 豆包返回文本: {text[:300]}...")
            
            # 尝试提取 JSON
            json_data = self._extract_json(text)
            
            if not json_data:
                logger.warning("⚠️ 无法从豆包返回中提取 JSON")
                return None
            
            # 构建识别结果
            return RecognitionResult(
                name=json_data.get("name", "未知食物"),
                confidence=float(json_data.get("confidence", 0.8)),
                category=json_data.get("category", "其他"),
                food_state=json_data.get("food_state"),
                cooking_method=json_data.get("cooking_method"),
                estimated_weight=json_data.get("estimated_weight_grams"),
                calories_per_100g=json_data.get("calories_per_100g"),
                total_calories_min=json_data.get("total_calories_min"),
                total_calories_max=json_data.get("total_calories_max"),
                nutrition=json_data.get("nutrition"),
                health_tips=json_data.get("health_tips"),
                analysis=json_data.get("analysis"),
                contraindications=json_data.get("contraindications"),
                ai_source="doubao",
            )
            
        except Exception as e:
            logger.error(f"❌ 解析豆包响应失败: {type(e).__name__}: {str(e)}")
            return None
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取 JSON 对象
        
        豆包可能返回带有 markdown 代码块的 JSON
        """
        # 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取 ```json ... ``` 代码块
        json_match = re.search(r'```(?:json)?\s*\n?([\s\S]*?)\n?```', text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试提取 { ... } 部分
        brace_match = re.search(r'\{[\s\S]*\}', text)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def _get_mock_results(self) -> List[RecognitionResult]:
        """返回模拟数据（未配置豆包AI时使用）"""
        return [
            RecognitionResult(
                name="宫保鸡丁",
                confidence=0.85,
                category="荤菜",
                cooking_method="爆炒",
                estimated_weight=250,
                calories_per_100g=180,
                total_calories_min=400,
                total_calories_max=500,
                nutrition={"protein": 20, "fat": 15, "carbohydrate": 12},
                health_tips="高蛋白菜品，但油脂含量较高，建议适量食用",
                analysis="这是一道经典川菜，使用鸡胸肉和花生爆炒而成",
                ai_source="mock",
            ),
        ]


# 全局单例
doubao_ai_service = DoubaoAIService()


async def generate_food_image(food_name: str, description: str = "") -> Optional[str]:
    """
    使用豆包 seedream 模型生成菜品图片

    Args:
        food_name: 菜品名称
        description: 菜品描述

    Returns:
        本地保存的图片路径，失败返回 None
    """
    import uuid
    from pathlib import Path

    image_model = getattr(settings, 'doubao_image_model', 'doubao-seedream-4-5-251128')
    api_key = settings.doubao_api_key
    base_url = settings.doubao_base_url or "https://ark.cn-beijing.volces.com/api/v3"

    if not api_key:
        logger.error("豆包AI未配置，无法生成图片")
        return None

    prompt = (
        f"一道精美的中式菜品摄影照片：{food_name}。"
        f"{description + '。' if description else ''}"
        f"专业美食摄影风格，俯拍45度角，自然光线，"
        f"白色瓷盘盛装，背景简洁干净，"
        f"色彩鲜艳诱人，高清细节，8K画质。"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": image_model,
        "prompt": prompt,
        "size": "1920x1920",
        "response_format": "url",
    }

    api_url = f"{base_url}/images/generations"
    logger.info(f"🎨 生成菜品图片: {food_name}, 模型: {image_model}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            if response.status_code != 200:
                logger.error(f"图片生成API错误: {response.status_code} - {response.text[:500]}")
                return None

            result = response.json()
            image_url = result["data"][0]["url"]

            save_dir = Path("static/uploads/recipes")
            save_dir.mkdir(parents=True, exist_ok=True)
            filename = f"{uuid.uuid4().hex[:12]}.jpg"
            filepath = save_dir / filename

            img_resp = await client.get(image_url, timeout=60.0)
            if img_resp.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(img_resp.content)
                local_path = f"/static/uploads/recipes/{filename}"
                logger.info(f"✅ 图片已保存: {local_path}")
                return local_path

            logger.error(f"图片下载失败: {img_resp.status_code}")
            return None
    except Exception as e:
        logger.error(f"图片生成失败: {type(e).__name__}: {e}")
        return None


def encode_image_to_base64(image_bytes: bytes) -> str:
    """将图片字节转换为 base64 编码"""
    return base64.b64encode(image_bytes).decode("utf-8")
