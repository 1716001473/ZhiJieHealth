# -*- coding: utf-8 -*-
"""
百度AI菜品识别服务封装
"""
import base64
from typing import List, Optional
import httpx

from app.config import get_settings
from app.schemas.recognition import RecognitionResult

settings = get_settings()


class BaiduAIService:
    """百度AI菜品识别服务"""
    
    # 百度AI API 地址
    TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    DISH_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v2/dish"
    FRUIT_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v1/classify/ingredient"
    PLANT_URL = "https://aip.baidubce.com/rest/2.0/image-classify/v1/plant"
    
    def __init__(self):
        self.api_key = settings.baidu_api_key
        self.secret_key = settings.baidu_secret_key
        self.access_token: Optional[str] = None
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置百度AI"""
        return bool(self.api_key and self.secret_key)
    
    async def get_access_token(self) -> str:
        """
        获取百度AI访问令牌
        令牌有效期30天，实际使用时应该缓存
        """
        if not self.is_configured:
            raise ValueError("百度AI未配置，请在 .env 文件中设置 BAIDU_API_KEY 和 BAIDU_SECRET_KEY")
        
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.TOKEN_URL, params=params)
            result = response.json()
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                return self.access_token
            else:
                raise ValueError(f"获取access_token失败: {result}")
    
    async def recognize_dish(self, image_base64: str, top_num: int = 5) -> List[RecognitionResult]:
        """
        识别菜品
        
        Args:
            image_base64: 图片的base64编码
            top_num: 返回结果数量，默认5
            
        Returns:
            识别结果列表
        """
        return await self._recognize_with_fallback(image_base64, top_num)

    async def _recognize_with_fallback(self, image_base64: str, top_num: int = 5) -> List[RecognitionResult]:
        """优先菜品识别，置信度不足时自动切换到果蔬/植物识别"""
        if not self.is_configured:
            print("⚠️ 百度AI未配置，使用模拟数据")
            return self._get_mock_results()

        dish_results = await self._request_recognition(
            url=self.DISH_URL,
            image_base64=image_base64,
            top_num=top_num,
            category_label="菜品识别",
            extra_data={"filter_threshold": 0.1},
        )

        fruit_results = await self._request_recognition(
            url=self.FRUIT_URL,
            image_base64=image_base64,
            top_num=top_num,
            category_label="果蔬识别",
        )

        plant_results = await self._request_recognition(
            url=self.PLANT_URL,
            image_base64=image_base64,
            top_num=top_num,
            category_label="植物识别",
        )

        merged_results = dish_results + fruit_results + plant_results
        if merged_results:
            sorted_results = sorted(merged_results, key=lambda x: x.confidence, reverse=True)
            
            # 策略优化：如果果蔬/食材识别有高置信度结果(>0.8)，优先推荐。
            # 解决菜品识别模型容易对生鲜食材产生高置信度误判的问题（如将西红柿误判为非菜）
            top_fruit = next((r for r in fruit_results if r.confidence > 0.8), None)
            
            if top_fruit and sorted_results[0] != top_fruit:
                # 将该高置信度果蔬结果提升到首位
                if top_fruit in sorted_results:
                    sorted_results.remove(top_fruit)
                sorted_results.insert(0, top_fruit)
                print(f"⚠️ 策略调整：优先展示导致信度果蔬结果 [{top_fruit.name}] (confidence: {top_fruit.confidence})")
            
            return sorted_results

        print("⚠️ 未识别到菜品/果蔬/植物，使用模拟数据")
        return self._get_mock_results()

    async def _request_recognition(
        self,
        url: str,
        image_base64: str,
        top_num: int,
        category_label: str,
        extra_data: Optional[dict] = None,
    ) -> List[RecognitionResult]:
        if not self.access_token:
            await self.get_access_token()
            print("✅ 获取 access_token 成功")

        request_url = f"{url}?access_token={self.access_token}"

        data = {
            "image": image_base64,
            "top_num": top_num,
        }
        if extra_data:
            data.update(extra_data)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        print(f"🔍 调用百度AI {category_label} API...")
        print(f"   URL: {url}")
        print(f"   图片大小: {len(image_base64)} 字符")

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                request_url,
                data=data,
                headers=headers,
            )
            result = response.json()

        print(f"📥 百度AI返回: {result}")

        result_list = result.get("result") or []
        result_count = result.get("result_num", len(result_list))
        if result_list and result_count > 0:
            recognition_results = []
            for item in result_list:
                prob_value = item.get("probability") or item.get("score") or item.get("confidence") or 0
                try:
                    probability = float(prob_value)
                except:
                    probability = 0.0

                baidu_calorie = item.get("calorie", None)

                recognition_results.append(
                    RecognitionResult(
                        name=item.get("name", "未知"),
                        confidence=probability,
                        category=category_label,
                        baidu_calorie=baidu_calorie,
                    )
                )
            print(f"✅ 识别成功，找到 {len(recognition_results)} 个结果")
            return recognition_results
        elif "error_code" in result:
            error_code = result["error_code"]
            error_msg = result.get("error_msg", "未知错误")
            print(f"❌ 百度AI错误: {error_code} - {error_msg}")

            if error_code in [110, 111]:
                self.access_token = None
                await self.get_access_token()
                return await self._request_recognition(
                    url=url,
                    image_base64=image_base64,
                    top_num=top_num,
                    category_label=category_label,
                    extra_data=extra_data,
                )

            return []

        return []
    
    def _get_mock_results(self) -> List[RecognitionResult]:
        """返回模拟数据（未配置百度AI时使用）"""
        return [
            RecognitionResult(name="宫保鸡丁", confidence=0.85, category="荤菜"),
            RecognitionResult(name="番茄炒蛋", confidence=0.08, category="荤菜"),
            RecognitionResult(name="鱼香肉丝", confidence=0.05, category="荤菜"),
        ]


# 全局单例
baidu_ai_service = BaiduAIService()


def encode_image_to_base64(image_bytes: bytes) -> str:
    """将图片字节转换为base64编码"""
    return base64.b64encode(image_bytes).decode("utf-8")
