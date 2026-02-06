# -*- coding: utf-8 -*-
"""
DeepSeek AI 服务封装
用于生成食物的营养数据和健康建议
"""
import json
import re
from typing import Optional, Dict, Any, List
import httpx

from app.config import get_settings

settings = get_settings()


class DeepSeekService:
    """DeepSeek AI 营养分析服务"""
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.model = "deepseek-chat"
    
    @property
    def is_configured(self) -> bool:
        """检查是否已配置"""
        return bool(self.api_key)
    
    async def get_nutrition_info(self, food_name: str, baidu_calorie: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        根据食物名称获取营养信息
        
        Args:
            food_name: 食物名称（如"小炒肉"）
            baidu_calorie: 百度返回的热量（可选，用于参考）
            
        Returns:
            营养信息字典，包含：
            - calories: 热量(kcal)
            - protein: 蛋白质(g)
            - fat: 脂肪(g)
            - carbohydrate: 碳水化合物(g)
            - gi: 血糖生成指数
            - health_rating: 健康评级
            - health_tips: 健康建议
            - contraindications: 禁忌人群列表
        """
        if not self.is_configured:
            print("⚠️ DeepSeek 未配置，跳过营养分析")
            return None

        # 构建 Prompt
        reference_hint = ""
        if baidu_calorie:
            reference_hint = f"\n参考：百度识别返回的热量约为 {baidu_calorie} kcal/100g，请以此作为参考。"

        prompt = f"""你是一位专业的营养学专家。请根据菜名"{food_name}"，提供以下营养和健康信息。{reference_hint}

请严格按照以下 JSON 格式返回（不要有任何其他文字）：
{{
  "calories": 数字（每100g热量，单位kcal，范围0-900）,
  "protein": 数字（每100g蛋白质，单位g，范围0-50）,
  "fat": 数字（每100g脂肪，单位g，范围0-80）,
  "carbohydrate": 数字（每100g碳水化合物，单位g，范围0-80）,
  "gi": 数字（血糖生成指数，范围0-100，若无法估算则写null）,
  "health_rating": "推荐" 或 "适量" 或 "少食",
  "health_tips": "一句话健康建议",
  "contraindications": [
    {{
      "condition_type": "人群类型（如糖尿病患者、高血压患者、痛风患者、孕妇等）",
      "severity": "禁食" 或 "慎食" 或 "少食",
      "reason": "原因说明"
    }}
  ]
}}

注意：
1. 数值必须是合理的数字，不能为负数
2. 热量不应超过 900 kcal/100g
3. 蛋白质、脂肪、碳水各自不应超过其合理最大值
4. 如果无法确定，请给出合理的估算值"""

        try:
            print(f"🤖 调用 DeepSeek 分析: {food_name}")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                    }
                )

                if response.status_code != 200:
                    print(f"❌ DeepSeek API 错误: {response.status_code} - {response.text}")
                    return None

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                print(f"📥 DeepSeek 返回: {content[:200]}...")

                # 解析 JSON
                nutrition_data = self._parse_json_response(content)

                if nutrition_data:
                    # 验证数据
                    validated_data = self._validate_nutrition_data(nutrition_data)
                    if validated_data:
                        print("✅ DeepSeek 分析完成")
                        return validated_data
                    else:
                        print("⚠️ 数据验证失败")
                        return None
                else:
                    print("⚠️ JSON 解析失败")
                    return None

        except Exception as e:
            print(f"❌ DeepSeek 异常: {type(e).__name__}: {str(e)}")
            return None

    async def get_health_advice(self, profile: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        根据健康档案获取饮食与运动建议

        Args:
            profile: 包含体重、身高、年龄、性别、活动水平等信息
        """
        if not self.is_configured:
            print("⚠️ DeepSeek 未配置，跳过健康建议生成")
            return None

        weight = profile.get("weight")
        height = profile.get("height")
        age = profile.get("age")
        gender = profile.get("gender")
        activity = profile.get("activity")

        prompt = f"""你是一位专业营养师和运动教练，请根据以下用户信息给出简洁建议：
体重：{weight} kg
身高：{height} cm
年龄：{age}
性别：{gender}
活动水平：{activity}

请严格返回以下 JSON 格式（不要任何其他文字）：
{{
  "diet_advice": "一句话饮食建议（30字以内）",
  "exercise_advice": "一句话运动建议（30字以内）"
}}

注意：
1. 内容要通俗、可执行
2. 若信息不足，请给出通用建议"""

        try:
            print("🤖 调用 DeepSeek 生成健康建议")

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.3,
                    }
                )

                if response.status_code != 200:
                    print(f"❌ DeepSeek API 错误: {response.status_code} - {response.text}")
                    return None

                result = response.json()
                content = result["choices"][0]["message"]["content"]

                print(f"📥 DeepSeek 建议: {content[:200]}...")

                advice_data = self._parse_json_response(content)
                if not advice_data:
                    print("⚠️ JSON 解析失败")
                    return None

                if "diet_advice" not in advice_data or "exercise_advice" not in advice_data:
                    print("⚠️ 建议字段缺失")
                    return None

                return advice_data

        except Exception as e:
            print(f"❌ DeepSeek 异常: {type(e).__name__}: {str(e)}")
            return None
    
    def _parse_json_response(self, content: str) -> Optional[Dict[str, Any]]:
        """从响应中解析 JSON"""
        try:
            # 1. 尝试清洗 Markdown 代码块
            cleaned_content = content
            if "```json" in content:
                pattern = r"```json\s*(\{[\s\S]*?\})\s*```"
                match = re.search(pattern, content)
                if match:
                    cleaned_content = match.group(1)
            elif "```" in content:
                pattern = r"```\s*(\{[\s\S]*?\})\s*```"
                match = re.search(pattern, content)
                if match:
                    cleaned_content = match.group(1)
            
            # 2. 尝试直接解析清洗后的内容
            return json.loads(cleaned_content)
        except json.JSONDecodeError:
            pass
        
        # 3. 兜底：使用正则贪婪匹配最外层 {}
        try:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
        except Exception:
            pass
            
        print(f"❌ JSON 解析最终失败. 内容预览: {content[:100]}...")
        return None
    
    def _validate_nutrition_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """验证营养数据的合理性"""
        try:
            # 必须字段
            required_fields = ["calories", "protein", "fat", "carbohydrate"]
            for field in required_fields:
                if field not in data:
                    print(f"⚠️ 缺少必须字段: {field}")
                    return None
            
            # 数值范围验证
            validations = {
                "calories": (0, 900),      # 热量不应超过 900 kcal/100g
                "protein": (0, 50),        # 蛋白质不应超过 50g/100g
                "fat": (0, 100),           # 脂肪不应超过 100g/100g（如纯油）
                "carbohydrate": (0, 100),  # 碳水不应超过 100g/100g
                "gi": (0, 100),            # GI 范围 0-100
            }
            
            for field, (min_val, max_val) in validations.items():
                if field in data and data[field] is not None:
                    value = float(data[field])
                    if value < min_val or value > max_val:
                        print(f"⚠️ {field} 值异常: {value}，范围应为 {min_val}-{max_val}")
                        # 修正为边界值
                        data[field] = max(min_val, min(value, max_val))
            
            # 确保 health_rating 有效
            valid_ratings = ["推荐", "适量", "少食"]
            if data.get("health_rating") not in valid_ratings:
                data["health_rating"] = "适量"
            
            # 确保 contraindications 是列表
            if not isinstance(data.get("contraindications"), list):
                data["contraindications"] = []
            
            return data
            
        except Exception as e:
            print(f"⚠️ 验证异常: {e}")
            return None

    async def generate_diet_plan(
        self,
        user_profile: str,
        goal: str,
        preferences: str,
        disliked_tags: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        生成7天推荐食谱

        Args:
            user_profile: 用户简况字符串 (如 "男性, 25岁, 70kg")
            goal: 健康目标 (如 "减脂", "增肌")
            preferences: 饮食偏好 (如 "不吃辣", "素食")
            disliked_tags: 用户不喜欢的标签列表 (如 ["芹菜", "海鲜", "复杂做法"])
        """
        if not self.is_configured:
            print("⚠️ DeepSeek 未配置，跳过食谱生成")
            return None

        prompt = f"""你是一位资深营养师。请根据以下用户情况，设计一份科学的【7天定制食谱】。
用户画像：{user_profile}
健康目标：{goal}
饮食偏好：{preferences}
"""

        # 核心：注入用户不喜欢的标签
        if disliked_tags and len(disliked_tags) > 0:
            disliked_str = "、".join(disliked_tags)
            prompt += f"""
⚠️ 用户历史反馈不喜欢：{disliked_str}
❗重要：请严格避开以上内容，不要推荐包含这些元素的食谱。
- 如果标签是食材（如"芹菜"、"海鲜"），绝对不使用该食材
- 如果标签是"复杂做法"，只推荐简单快手菜
- 如果标签是"高热量"，只推荐低热量健康菜
- 如果标签是"油炸"、"辣"等做法，避免相关烹饪方式
"""

        prompt += """
请直接返回满足 strict JSON 格式的数据，不要包裹markdown标记，JSON结构如下：
{
  "name": "食谱名称（如：高效减脂7日计划）",
  "description": "简短的推荐理由（50字以内）",
  "tags": ["减脂", "低碳水"], // 请从以下标签中选择1-3个：减脂, 增肌, 低碳水, 高蛋白, 素食, 快速
  "days": [
    {
      "day_index": 1,
      "title": "每日主题（如：排毒清肠日）",
      "meals": [
        {
          "meal_type": "breakfast/lunch/dinner/snack",
          "food_name": "具体食物名（通俗易懂）",
          "amount_desc": "份量描述（支持普通单位，如1碗、200g、1个）",
          "calories": 估算热量(int)
        }
      ]
    }
  ]
}

要求：
1. 必须包含完整7天数据。
2. 每天必须包含早(breakfast)、午(lunch)、晚(dinner)三餐，加餐(snack)可选。
3. 确保热量和营养搭配符合用户"{goal}"的目标。
4. 【重要】严格遵守用户的"饮食偏好"。例如：若用户"乳糖不耐受"，则绝对不能出现牛奶、酸奶等乳制品；若"素食"，则不能出现肉类。
5. 食材要常见易获得，做法简单。
6. tags 字段必须且仅能包含以下词汇：减脂, 增肌, 低碳水, 高蛋白, 素食, 快速。根据食谱特点选择最匹配的1-3个。
7. 请确保JSON格式合法的 List/Dict 嵌套，不要包含注释。"""

        try:
            if disliked_tags and len(disliked_tags) > 0:
                print(f"🤖 调用 DeepSeek 生成食谱: {goal} | 用户不喜欢: {', '.join(disliked_tags)}")
            else:
                print(f"🤖 调用 DeepSeek 生成食谱: {goal}")

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.5,
                        "max_tokens": 4000
                    }
                )

                if response.status_code != 200:
                    print(f"❌ DeepSeek API 错误: {response.status_code} - {response.text}")
                    return None

                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # 解析 JSON
                plan_data = self._parse_json_response(content)
                
                if plan_data:
                    # 清洗数据（处理可能的格式问题）
                    plan_data = self._clean_diet_plan_data(plan_data)
                    
                    # 验证数据
                    if self._validate_diet_plan_data(plan_data):
                        print("✅ DeepSeek 食谱生成完成")
                        return plan_data
                    else:
                        print("⚠️ 食谱数据结构校验失败")
                        return None
                else:
                    print("⚠️ JSON 解析失败")
                    return None

        except Exception as e:
            print(f"❌ DeepSeek 异常: {type(e).__name__}: {str(e)}")
            return None

    def _clean_diet_plan_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清洗食谱数据，处理非标准格式"""
        try:
            import re
            
            if "days" in data and isinstance(data["days"], list):
                for day in data["days"]:
                    if "meals" in day and isinstance(day["meals"], list):
                        for meal in day["meals"]:
                            # 清洗 calories
                            if "calories" in meal:
                                raw_cal = meal["calories"]
                                if isinstance(raw_cal, str):
                                    # 提取数字
                                    match = re.search(r'\d+', raw_cal)
                                    if match:
                                        meal["calories"] = int(match.group())
                                    else:
                                        meal["calories"] = 0
                                elif not isinstance(raw_cal, (int, float)):
                                     meal["calories"] = 0
                                else:
                                     meal["calories"] = int(raw_cal)
                            
                            # Clean string fields
                            if "food_name" in meal and isinstance(meal["food_name"], str):
                                meal["food_name"] = meal["food_name"][:100]
                            if "amount_desc" in meal and isinstance(meal["amount_desc"], str):
                                meal["amount_desc"] = meal["amount_desc"][:50]
                                     
            return data
        except Exception as e:
            print(f"⚠️ 数据清洗异常: {e}")
            return data

    def _validate_diet_plan_data(self, data: Dict[str, Any]) -> bool:
        """验证食谱数据结构"""
        try:
            if "days" not in data or not isinstance(data["days"], list):
                return False
            
            if len(data["days"]) == 0:
                print("⚠️ 天数为空")
                return False

            for day in data["days"]:
                if "meals" not in day or not isinstance(day["meals"], list):
                    return False
                
                for meal in day["meals"]:
                    required = ["meal_type", "food_name"]
                    if not all(k in meal for k in required):
                        return False
            
            if "tags" in data:
                if not isinstance(data["tags"], list):
                    data["tags"] = []
                else:
                    # Enforce string types
                    data["tags"] = [str(t) for t in data["tags"] if isinstance(t, (str, int))]
            
            return True
        except Exception:
            return False


# 全局单例
deepseek_service = DeepSeekService()
