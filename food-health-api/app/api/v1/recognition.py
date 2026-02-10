# -*- coding: utf-8 -*-
"""
食物识别 API 路由
优先使用豆包 AI，未配置时降级到百度 AI
"""
import logging
import os
import uuid
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.doubao_ai import doubao_ai_service, encode_image_to_base64
from app.services.baidu_ai import baidu_ai_service
from app.services.deepseek_service import deepseek_service
from app.services.food_service import FoodService
from app.schemas.response import APIResponse
from app.schemas.recognition import RecognizeResponse, RecognitionTopResult
from app.schemas.food import NutritionInfo, ContraindicationInfo
from app.config import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()
settings = get_settings()

# 图片保存目录
UPLOAD_DIR = Path("static/uploads/recognition")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_recognition_image(image_bytes: bytes, content_type: str) -> str:
    """
    保存识别图片到服务器
    
    Returns:
        保存后的图片相对路径（可通过 /static/... 访问）
    """
    # 生成唯一文件名
    ext = ".jpg"
    if content_type == "image/png":
        ext = ".png"
    elif content_type == "image/bmp":
        ext = ".bmp"
    
    # 按日期分目录
    date_dir = datetime.now().strftime("%Y%m%d")
    save_dir = UPLOAD_DIR / date_dir
    save_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = save_dir / filename
    
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    
    # 返回相对路径
    return f"/static/uploads/recognition/{date_dir}/{filename}"


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
    
    识别服务优先级：豆包 AI > 百度 AI > 模拟数据
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
    
    # 保存图片
    saved_image_url = save_recognition_image(image_bytes, image.content_type)
    logger.info(f"📸 图片已保存: {saved_image_url}")
    
    # 转换为 base64
    image_base64 = encode_image_to_base64(image_bytes)
    
    # 选择识别服务：优先豆包，降级百度
    ai_source = None
    results = []
    
    if settings.doubao_configured:
        # 使用豆包 AI
        try:
            logger.info("🔍 使用豆包 AI 进行识别...")
            results = await doubao_ai_service.recognize_food(image_base64)
            ai_source = "doubao"
        except Exception as e:
            logger.warning(f"豆包AI调用失败，降级到百度AI: {type(e).__name__}: {str(e)}")
            ai_source = None
    
    if not results and settings.baidu_ai_configured:
        # 降级到百度 AI
        try:
            logger.info("🔍 使用百度 AI 进行识别...")
            results = await baidu_ai_service.recognize_dish(image_base64)
            ai_source = "baidu"
        except Exception as e:
            logger.warning(f"百度AI调用失败: {type(e).__name__}: {str(e)}")
    
    if not results:
        # 都失败了，返回空结果
        return APIResponse.success(
            data=RecognizeResponse(
                results=[],
                top_result=None,
                image_url=saved_image_url,
                message="未能识别出食物，请尝试更清晰的图片",
            )
        )
    
    # 获取最佳匹配的详细信息
    top_result = results[0]
    food_service = FoodService(db)
    
    # 构建详细结果
    top_result_detail = await _build_top_result_detail(
        top_result, food_service, ai_source, db
    )
    
    # 构建响应
    is_mock = not (settings.doubao_configured or settings.baidu_ai_configured)
    message = "识别成功"
    if is_mock:
        message = "（使用模拟数据）识别结果仅供演示"
    elif ai_source == "doubao":
        message = "识别成功（豆包AI）"
    elif ai_source == "baidu":
        message = "识别成功（百度AI）"
    
    return APIResponse.success(
        data=RecognizeResponse(
            results=results,
            top_result=top_result_detail,
            image_url=saved_image_url,
            message=message,
            is_mock=is_mock,
        )
    )


async def _build_top_result_detail(
    top_result, food_service: FoodService, ai_source: str, db: Session
) -> RecognitionTopResult:
    """
    构建识别结果详情
    
    优先使用豆包返回的完整信息，
    如果是百度识别则补充 DeepSeek 分析
    """
    # 先查本地数据库
    food_detail = food_service.get_food_response(top_result.name)
    
    if food_detail:
        # 数据库有数据，使用数据库信息
        return RecognitionTopResult(
            name=top_result.name,
            confidence=top_result.confidence,
            category=food_detail.category,
            food_state=getattr(top_result, 'food_state', None),
            baidu_calorie=getattr(top_result, 'baidu_calorie', None),
            cooking_method=getattr(top_result, 'cooking_method', None),
            estimated_weight=getattr(top_result, 'estimated_weight', None),
            calories_per_100g=getattr(top_result, 'calories_per_100g', None),
            total_calories_min=getattr(top_result, 'total_calories_min', None),
            total_calories_max=getattr(top_result, 'total_calories_max', None),
            analysis=getattr(top_result, 'analysis', None),
            nutrition=food_detail.nutrition,
            health_rating=food_detail.health_rating,
            health_tips=food_detail.health_tips or getattr(top_result, 'health_tips', None),
            contraindications=food_detail.contraindications,
            found_in_database=True,
            ai_generated=False,
            ai_source=ai_source,
        )
    
    # 如果是豆包识别，豆包已经返回了丰富信息
    if ai_source == "doubao" and hasattr(top_result, 'nutrition') and top_result.nutrition:
        nutrition_dict = top_result.nutrition
        nutrition_info = NutritionInfo(
            calories=top_result.calories_per_100g or 0,
            protein=nutrition_dict.get("protein", 0),
            fat=nutrition_dict.get("fat", 0),
            carbohydrate=nutrition_dict.get("carbohydrate", 0),
        )
        
        # 缓存到临时表
        food_service.upsert_temp_food(
            name=top_result.name,
            nutrition={
                "calories": nutrition_info.calories,
                "protein": nutrition_info.protein,
                "fat": nutrition_info.fat,
                "carb": nutrition_info.carbohydrate,
            },
            source="doubao_ai",
        )
        
        # 解析豆包返回的不适宜人群
        contraindications = []
        raw_contraindications = getattr(top_result, 'contraindications', None) or []
        for item in raw_contraindications:
            if isinstance(item, dict):
                contraindications.append(ContraindicationInfo(
                    condition_type=item.get("condition", item.get("condition_type", "")),
                    severity=item.get("severity", "少食"),
                    reason=item.get("reason", ""),
                    suggestion=item.get("advice", item.get("suggestion", "")),
                ))
        
        return RecognitionTopResult(
            name=top_result.name,
            confidence=top_result.confidence,
            category=top_result.category or "AI分析",
            food_state=getattr(top_result, 'food_state', None),
            cooking_method=top_result.cooking_method,
            estimated_weight=top_result.estimated_weight,
            calories_per_100g=top_result.calories_per_100g,
            total_calories_min=top_result.total_calories_min,
            total_calories_max=top_result.total_calories_max,
            analysis=top_result.analysis,
            nutrition=nutrition_info,
            health_tips=top_result.health_tips,
            contraindications=contraindications,
            found_in_database=False,
            ai_generated=True,
            ai_source="doubao",
        )
    
    # 百度识别或豆包信息不完整，尝试 DeepSeek 补充
    baidu_calorie = getattr(top_result, 'baidu_calorie', None)
    ai_nutrition = await deepseek_service.get_nutrition_info(
        top_result.name, 
        baidu_calorie
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
        
        return RecognitionTopResult(
            name=top_result.name,
            confidence=top_result.confidence,
            category=top_result.category or "AI分析",
            baidu_calorie=baidu_calorie,
            nutrition=nutrition_info,
            gi=ai_nutrition.get("gi"),
            health_rating=ai_nutrition.get("health_rating"),
            health_tips=ai_nutrition.get("health_tips"),
            contraindications=contraindications,
            found_in_database=False,
            ai_generated=True,
            ai_source=ai_source or "deepseek",
        )
    
    # DeepSeek 也不可用，降级显示基本信息
    if baidu_calorie:
        food_service.upsert_temp_food(
            name=top_result.name,
            nutrition={
                "calories": float(baidu_calorie) if baidu_calorie else 0,
                "protein": 0,
                "fat": 0,
                "carb": 0,
            },
            source="baidu_ai",
        )
    
    return RecognitionTopResult(
        name=top_result.name,
        confidence=top_result.confidence,
        category=top_result.category,
        baidu_calorie=baidu_calorie,
        found_in_database=False,
        ai_generated=False,
        ai_source=ai_source,
    )
