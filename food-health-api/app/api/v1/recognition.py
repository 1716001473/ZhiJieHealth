# -*- coding: utf-8 -*-
"""
食物识别 API 路由
"""
import logging

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.baidu_ai import baidu_ai_service, encode_image_to_base64
from app.services.deepseek_service import deepseek_service
from app.services.food_service import FoodService
from app.schemas.response import APIResponse
from app.schemas.recognition import RecognizeResponse, RecognitionTopResult
from app.schemas.food import NutritionInfo, ContraindicationInfo
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()


@router.post("/recognize", response_model=APIResponse[RecognizeResponse])
async def recognize_food(
    image: UploadFile = File(..., description="食物图片"),
    db: Session = Depends(get_db),
):
    """
    识别食物图片
    
    上传一张食物图片，返回识别结果和营养信息
    
    - **image**: 图片文件（支持 jpg, png, bmp 格式）
    
    返回数据包含：
    - **results**: 识别结果列表（按置信度排序）
    - **top_result**: 最佳匹配结果的详细信息（营养、健康建议、禁忌）
    """
    # 验证文件类型
    if image.content_type not in ["image/jpeg", "image/png", "image/bmp"]:
        raise HTTPException(status_code=400, detail="仅支持 jpg, png, bmp 格式的图片")
    
    # 读取图片内容
    image_bytes = await image.read()
    logger.info(f"收到图片: {image.filename}, 大小: {len(image_bytes)} bytes, 类型: {image.content_type}")
    
    # 限制图片大小（4MB）
    if len(image_bytes) > 4 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 4MB")
    
    # 转换为 base64
    image_base64 = encode_image_to_base64(image_bytes)
    logger.info(f"Base64 编码后大小: {len(image_base64)} 字符")
    
    # 调用百度AI识别
    try:
        results = await baidu_ai_service.recognize_dish(image_base64)
    except Exception as e:
        logger.warning(f"识别异常: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")
    
    if not results:
        return APIResponse.success(
            data=RecognizeResponse(
                results=[],
                top_result=None,
                message="未能识别出食物，请尝试更清晰的图片",
            )
        )
    
    # 获取最佳匹配的详细信息
    top_result = results[0]
    food_service = FoodService(db)
    food_detail = food_service.get_food_response(top_result.name)
    
    if food_detail:
        top_result_detail = RecognitionTopResult(
            name=top_result.name,
            confidence=top_result.confidence,
            category=food_detail.category,
            baidu_calorie=top_result.baidu_calorie,
            nutrition=food_detail.nutrition,
            health_rating=food_detail.health_rating,
            health_tips=food_detail.health_tips,
            contraindications=food_detail.contraindications,
            found_in_database=True,
            ai_generated=False,
        )
    else:
        # 数据库中没有该食物的详细信息，尝试使用 DeepSeek 生成
        ai_nutrition = await deepseek_service.get_nutrition_info(
            top_result.name, 
            top_result.baidu_calorie
        )
        
        if ai_nutrition:
            food_service.upsert_temp_food(
                name=top_result.name,
                nutrition={
                    "calories": ai_nutrition.get("calories", 0),
                    "protein": ai_nutrition.get("protein", 0),
                    "fat": ai_nutrition.get("fat", 0),
                    "carb": ai_nutrition.get("carbohydrate", 0),
                },
                source="deepseek_ai",
            )
            # DeepSeek 返回了数据
            nutrition_info = NutritionInfo(
                calories=ai_nutrition.get("calories", 0),
                protein=ai_nutrition.get("protein", 0),
                fat=ai_nutrition.get("fat", 0),
                carbohydrate=ai_nutrition.get("carbohydrate", 0),
            )
            
            # 解析禁忌人群
            contraindications = []
            for item in ai_nutrition.get("contraindications", []):
                contraindications.append(ContraindicationInfo(
                    condition_type=item.get("condition_type", ""),
                    severity=item.get("severity", "少食"),
                    reason=item.get("reason", ""),
                ))
            
            top_result_detail = RecognitionTopResult(
                name=top_result.name,
                confidence=top_result.confidence,
                category=top_result.category or "AI分析",
                baidu_calorie=top_result.baidu_calorie,
                nutrition=nutrition_info,
                gi=ai_nutrition.get("gi"),
                health_rating=ai_nutrition.get("health_rating"),
                health_tips=ai_nutrition.get("health_tips"),
                contraindications=contraindications,
                found_in_database=False,
                ai_generated=True,
            )
        else:
            # DeepSeek 不可用，降级为仅显示百度热量
            if top_result.baidu_calorie:
                food_service.upsert_temp_food(
                    name=top_result.name,
                    nutrition={
                        "calories": top_result.baidu_calorie,
                        "protein": 0,
                        "fat": 0,
                        "carb": 0,
                    },
                    source="baidu_ai",
                )
            top_result_detail = RecognitionTopResult(
                name=top_result.name,
                confidence=top_result.confidence,
                category=top_result.category,
                baidu_calorie=top_result.baidu_calorie,
                found_in_database=False,
                ai_generated=False,
            )
    
    # 构建响应
    is_mock = not settings.baidu_ai_configured
    message = "识别成功" if not is_mock else "（使用模拟数据）识别结果仅供演示"
    
    return APIResponse.success(
        data=RecognizeResponse(
            results=results,
            top_result=top_result_detail,
            message=message,
            is_mock=is_mock,
        )
    )
