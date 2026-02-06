# -*- coding: utf-8 -*-
"""
中国常见食材数据
基于《中国食物成分表》整理
"""
from sqlalchemy.orm import Session
from app.models.food import Food


# 中国常见食材数据（每100g营养成分）
CHINESE_FOODS = [
    # ===== 叶菜类 =====
    {"name": "娃娃菜", "alias": "小白菜,迷你白菜", "category": "蔬菜",
     "calories": 12, "protein": 1.5, "fat": 0.2, "carbohydrate": 1.8,
     "fiber": 1.0, "sodium": 57, "sugar": 1.2,
     "health_rating": "推荐", "health_tips": "低热量高纤维，减肥佳品"},

    {"name": "大白菜", "alias": "白菜,黄芽白", "category": "蔬菜",
     "calories": 17, "protein": 1.5, "fat": 0.1, "carbohydrate": 3.1,
     "fiber": 0.8, "sodium": 69, "sugar": 1.8,
     "health_rating": "推荐", "health_tips": "富含维生素C，冬季常见蔬菜"},

    {"name": "小白菜", "alias": "青菜,油菜", "category": "蔬菜",
     "calories": 15, "protein": 1.5, "fat": 0.3, "carbohydrate": 2.0,
     "fiber": 1.1, "sodium": 73, "sugar": 1.1,
     "health_rating": "推荐", "health_tips": "钙含量较高，适合日常食用"},

    {"name": "菠菜", "alias": "波斯菜,红根菜", "category": "蔬菜",
     "calories": 24, "protein": 2.6, "fat": 0.3, "carbohydrate": 3.6,
     "fiber": 1.7, "sodium": 85, "sugar": 0.4,
     "health_rating": "推荐", "health_tips": "富含铁和叶酸，但草酸含量高，建议焯水"},

    {"name": "生菜", "alias": "莴苣叶,叶用莴苣", "category": "蔬菜",
     "calories": 13, "protein": 1.3, "fat": 0.3, "carbohydrate": 1.9,
     "fiber": 0.7, "sodium": 13, "sugar": 0.9,
     "health_rating": "推荐", "health_tips": "水分充足，适合生食"},

    {"name": "油麦菜", "alias": "莜麦菜,苦菜", "category": "蔬菜",
     "calories": 15, "protein": 1.4, "fat": 0.4, "carbohydrate": 2.1,
     "fiber": 0.6, "sodium": 8, "sugar": 0.8,
     "health_rating": "推荐", "health_tips": "口感清脆，营养丰富"},

    {"name": "空心菜", "alias": "蕹菜,通菜", "category": "蔬菜",
     "calories": 20, "protein": 2.2, "fat": 0.3, "carbohydrate": 2.8,
     "fiber": 1.4, "sodium": 94, "sugar": 0.5,
     "health_rating": "推荐", "health_tips": "夏季时令蔬菜，清热解毒"},

    {"name": "韭菜", "alias": "起阳草,壮阳草", "category": "蔬菜",
     "calories": 26, "protein": 2.4, "fat": 0.4, "carbohydrate": 4.6,
     "fiber": 1.4, "sodium": 8, "sugar": 1.6,
     "health_rating": "适量", "health_tips": "温补食材，胃病患者慎食"},

    {"name": "芹菜", "alias": "旱芹,药芹", "category": "蔬菜",
     "calories": 14, "protein": 0.8, "fat": 0.1, "carbohydrate": 2.8,
     "fiber": 1.2, "sodium": 159, "sugar": 1.3,
     "health_rating": "推荐", "health_tips": "富含膳食纤维，有助降血压"},

    {"name": "茼蒿", "alias": "蓬蒿,菊花菜", "category": "蔬菜",
     "calories": 21, "protein": 1.9, "fat": 0.3, "carbohydrate": 3.9,
     "fiber": 1.2, "sodium": 172, "sugar": 0.8,
     "health_rating": "推荐", "health_tips": "火锅常用蔬菜，清香可口"},

    # ===== 瓜果类 =====
    {"name": "黄瓜", "alias": "胡瓜,青瓜", "category": "蔬菜",
     "calories": 15, "protein": 0.8, "fat": 0.2, "carbohydrate": 2.9,
     "fiber": 0.5, "sodium": 4, "sugar": 1.7,
     "health_rating": "推荐", "health_tips": "水分充足，适合生食或凉拌"},

    {"name": "西红柿", "alias": "番茄,洋柿子", "category": "蔬菜",
     "calories": 19, "protein": 0.9, "fat": 0.2, "carbohydrate": 4.0,
     "fiber": 0.5, "sodium": 5, "sugar": 2.6,
     "health_rating": "推荐", "health_tips": "富含番茄红素，抗氧化佳品"},

    {"name": "茄子", "alias": "落苏,矮瓜", "category": "蔬菜",
     "calories": 21, "protein": 1.1, "fat": 0.2, "carbohydrate": 4.9,
     "fiber": 1.3, "sodium": 5, "sugar": 2.4,
     "health_rating": "适量", "health_tips": "吸油性强，烹饪时注意用油量"},

    {"name": "冬瓜", "alias": "白瓜,东瓜", "category": "蔬菜",
     "calories": 11, "protein": 0.4, "fat": 0.2, "carbohydrate": 2.6,
     "fiber": 0.7, "sodium": 2, "sugar": 1.2,
     "health_rating": "推荐", "health_tips": "利尿消肿，夏季消暑佳品"},

    {"name": "南瓜", "alias": "倭瓜,番瓜", "category": "蔬菜",
     "calories": 22, "protein": 0.7, "fat": 0.1, "carbohydrate": 5.3,
     "fiber": 0.8, "sodium": 0.8, "sugar": 2.8,
     "health_rating": "推荐", "health_tips": "富含胡萝卜素，对眼睛有益"},

    {"name": "苦瓜", "alias": "凉瓜,癞葡萄", "category": "蔬菜",
     "calories": 19, "protein": 1.0, "fat": 0.1, "carbohydrate": 4.9,
     "fiber": 1.4, "sodium": 2, "sugar": 1.5,
     "health_rating": "推荐", "health_tips": "清热解毒，糖尿病患者适宜"},

    {"name": "丝瓜", "alias": "天罗,布瓜", "category": "蔬菜",
     "calories": 20, "protein": 1.0, "fat": 0.2, "carbohydrate": 4.2,
     "fiber": 0.6, "sodium": 5, "sugar": 2.1,
     "health_rating": "推荐", "health_tips": "清热化痰，夏季时令蔬菜"},

    {"name": "西葫芦", "alias": "角瓜,白瓜", "category": "蔬菜",
     "calories": 18, "protein": 0.8, "fat": 0.2, "carbohydrate": 3.8,
     "fiber": 0.6, "sodium": 3, "sugar": 2.2,
     "health_rating": "推荐", "health_tips": "低热量蔬菜，适合减肥"},

    # ===== 根茎类 =====
    {"name": "土豆", "alias": "马铃薯,洋芋", "category": "蔬菜",
     "calories": 76, "protein": 2.0, "fat": 0.2, "carbohydrate": 17.2,
     "fiber": 0.7, "sodium": 2.7, "sugar": 0.8,
     "health_rating": "适量", "health_tips": "淀粉含量高，可替代部分主食"},

    {"name": "红薯", "alias": "地瓜,番薯", "category": "蔬菜",
     "calories": 99, "protein": 1.1, "fat": 0.2, "carbohydrate": 24.7,
     "fiber": 1.6, "sodium": 28, "sugar": 5.6,
     "health_rating": "适量", "health_tips": "富含膳食纤维，但糖分较高"},

    {"name": "胡萝卜", "alias": "红萝卜,甘荀", "category": "蔬菜",
     "calories": 37, "protein": 1.0, "fat": 0.2, "carbohydrate": 8.8,
     "fiber": 1.1, "sodium": 71, "sugar": 4.7,
     "health_rating": "推荐", "health_tips": "富含胡萝卜素，护眼佳品"},

    {"name": "白萝卜", "alias": "莱菔,萝卜", "category": "蔬菜",
     "calories": 21, "protein": 0.9, "fat": 0.1, "carbohydrate": 5.0,
     "fiber": 1.0, "sodium": 61, "sugar": 2.5,
     "health_rating": "推荐", "health_tips": "消食化痰，冬季养生佳品"},

    {"name": "莲藕", "alias": "藕,莲菜", "category": "蔬菜",
     "calories": 70, "protein": 1.9, "fat": 0.2, "carbohydrate": 16.4,
     "fiber": 1.2, "sodium": 44, "sugar": 3.1,
     "health_rating": "适量", "health_tips": "生吃清热，熟吃补血"},

    {"name": "山药", "alias": "淮山,薯蓣", "category": "蔬菜",
     "calories": 56, "protein": 1.9, "fat": 0.2, "carbohydrate": 12.4,
     "fiber": 0.8, "sodium": 18, "sugar": 1.5,
     "health_rating": "推荐", "health_tips": "健脾养胃，药食同源"},

    {"name": "芋头", "alias": "芋艿,毛芋", "category": "蔬菜",
     "calories": 79, "protein": 2.2, "fat": 0.2, "carbohydrate": 18.1,
     "fiber": 1.0, "sodium": 33, "sugar": 0.8,
     "health_rating": "适量", "health_tips": "淀粉含量高，可替代主食"},

    {"name": "洋葱", "alias": "圆葱,玉葱", "category": "蔬菜",
     "calories": 39, "protein": 1.1, "fat": 0.2, "carbohydrate": 9.0,
     "fiber": 0.9, "sodium": 4, "sugar": 4.2,
     "health_rating": "推荐", "health_tips": "杀菌消炎，软化血管"},

    {"name": "大蒜", "alias": "蒜头,胡蒜", "category": "蔬菜",
     "calories": 126, "protein": 4.5, "fat": 0.2, "carbohydrate": 27.6,
     "fiber": 1.1, "sodium": 19, "sugar": 1.0,
     "health_rating": "适量", "health_tips": "杀菌抗病毒，但刺激性强"},

    {"name": "生姜", "alias": "姜,鲜姜", "category": "蔬菜",
     "calories": 41, "protein": 1.3, "fat": 0.6, "carbohydrate": 10.3,
     "fiber": 0.8, "sodium": 14, "sugar": 1.7,
     "health_rating": "适量", "health_tips": "驱寒暖胃，烹饪调味佳品"},

    # ===== 豆类/菌菇 =====
    {"name": "豆腐", "alias": "水豆腐,嫩豆腐", "category": "豆制品",
     "calories": 81, "protein": 8.1, "fat": 3.7, "carbohydrate": 4.2,
     "fiber": 0.4, "sodium": 7, "sugar": 0.9,
     "health_rating": "推荐", "health_tips": "优质植物蛋白来源"},

    {"name": "豆腐干", "alias": "豆干,香干", "category": "豆制品",
     "calories": 140, "protein": 16.2, "fat": 7.0, "carbohydrate": 4.9,
     "fiber": 0.8, "sodium": 584, "sugar": 0.5,
     "health_rating": "适量", "health_tips": "蛋白质丰富，但钠含量较高"},

    {"name": "豆芽", "alias": "黄豆芽,绿豆芽", "category": "蔬菜",
     "calories": 18, "protein": 2.1, "fat": 0.1, "carbohydrate": 2.9,
     "fiber": 0.8, "sodium": 7, "sugar": 0.8,
     "health_rating": "推荐", "health_tips": "富含维生素C，清热解毒"},

    {"name": "香菇", "alias": "冬菇,花菇", "category": "菌菇",
     "calories": 26, "protein": 2.2, "fat": 0.3, "carbohydrate": 5.2,
     "fiber": 3.3, "sodium": 11, "sugar": 1.4,
     "health_rating": "推荐", "health_tips": "增强免疫力，鲜美可口"},

    {"name": "金针菇", "alias": "金菇,毛柄金钱菌", "category": "菌菇",
     "calories": 32, "protein": 2.4, "fat": 0.4, "carbohydrate": 6.0,
     "fiber": 2.7, "sodium": 4, "sugar": 0.9,
     "health_rating": "推荐", "health_tips": "火锅必备，益智健脑"},

    {"name": "木耳", "alias": "黑木耳,云耳", "category": "菌菇",
     "calories": 21, "protein": 1.5, "fat": 0.2, "carbohydrate": 6.0,
     "fiber": 2.6, "sodium": 48, "sugar": 0.5,
     "health_rating": "推荐", "health_tips": "清肺润肠，补血养颜"},

    {"name": "平菇", "alias": "侧耳,秀珍菇", "category": "菌菇",
     "calories": 20, "protein": 1.9, "fat": 0.3, "carbohydrate": 4.6,
     "fiber": 2.3, "sodium": 8, "sugar": 1.1,
     "health_rating": "推荐", "health_tips": "价格实惠，营养丰富"},

    {"name": "杏鲍菇", "alias": "刺芹菇,雪茸", "category": "菌菇",
     "calories": 31, "protein": 1.3, "fat": 0.1, "carbohydrate": 8.3,
     "fiber": 1.8, "sodium": 4, "sugar": 1.5,
     "health_rating": "推荐", "health_tips": "口感似鲍鱼，素食佳品"},

    # ===== 肉类 =====
    {"name": "猪肉", "alias": "猪瘦肉,里脊肉", "category": "肉类",
     "calories": 143, "protein": 20.3, "fat": 6.2, "carbohydrate": 1.5,
     "fiber": 0, "sodium": 57, "sugar": 0,
     "health_rating": "适量", "health_tips": "优质蛋白来源，选择瘦肉更健康"},

    {"name": "五花肉", "alias": "三层肉,肋条肉", "category": "肉类",
     "calories": 395, "protein": 14.0, "fat": 37.0, "carbohydrate": 1.5,
     "fiber": 0, "sodium": 59, "sugar": 0,
     "health_rating": "少食", "health_tips": "脂肪含量高，高血脂者慎食"},

    {"name": "鸡胸肉", "alias": "鸡脯肉,鸡柳", "category": "肉类",
     "calories": 133, "protein": 19.4, "fat": 5.0, "carbohydrate": 2.5,
     "fiber": 0, "sodium": 64, "sugar": 0,
     "health_rating": "推荐", "health_tips": "高蛋白低脂肪，健身首选"},

    {"name": "鸡腿肉", "alias": "鸡腿,琵琶腿", "category": "肉类",
     "calories": 181, "protein": 16.0, "fat": 13.0, "carbohydrate": 0,
     "fiber": 0, "sodium": 90, "sugar": 0,
     "health_rating": "适量", "health_tips": "肉质鲜嫩，去皮更健康"},

    {"name": "牛肉", "alias": "黄牛肉,牛腩", "category": "肉类",
     "calories": 125, "protein": 19.9, "fat": 4.2, "carbohydrate": 2.0,
     "fiber": 0, "sodium": 84, "sugar": 0,
     "health_rating": "推荐", "health_tips": "富含铁和锌，补血佳品"},

    {"name": "羊肉", "alias": "绵羊肉,山羊肉", "category": "肉类",
     "calories": 203, "protein": 19.0, "fat": 14.1, "carbohydrate": 0,
     "fiber": 0, "sodium": 80, "sugar": 0,
     "health_rating": "适量", "health_tips": "温补食材，冬季进补佳品"},

    {"name": "鸭肉", "alias": "鸭子,水鸭", "category": "肉类",
     "calories": 240, "protein": 15.5, "fat": 19.7, "carbohydrate": 0.2,
     "fiber": 0, "sodium": 69, "sugar": 0,
     "health_rating": "适量", "health_tips": "滋阴清热，夏季食用佳"},

    # ===== 水产 =====
    {"name": "草鱼", "alias": "鲩鱼,混子", "category": "水产",
     "calories": 113, "protein": 16.6, "fat": 5.2, "carbohydrate": 0,
     "fiber": 0, "sodium": 46, "sugar": 0,
     "health_rating": "推荐", "health_tips": "淡水鱼常见品种，肉质鲜美"},

    {"name": "鲫鱼", "alias": "鲋鱼,喜头", "category": "水产",
     "calories": 108, "protein": 17.1, "fat": 4.1, "carbohydrate": 0,
     "fiber": 0, "sodium": 41, "sugar": 0,
     "health_rating": "推荐", "health_tips": "适合煲汤，产妇催乳佳品"},

    {"name": "带鱼", "alias": "刀鱼,裙带鱼", "category": "水产",
     "calories": 127, "protein": 17.7, "fat": 4.9, "carbohydrate": 3.1,
     "fiber": 0, "sodium": 150, "sugar": 0,
     "health_rating": "推荐", "health_tips": "富含DHA，健脑益智"},

    {"name": "虾仁", "alias": "河虾仁,海虾仁", "category": "水产",
     "calories": 48, "protein": 10.4, "fat": 0.5, "carbohydrate": 0,
     "fiber": 0, "sodium": 133, "sugar": 0,
     "health_rating": "推荐", "health_tips": "高蛋白低脂肪，痛风患者慎食"},

    {"name": "基围虾", "alias": "刀额新对虾,沙虾", "category": "水产",
     "calories": 101, "protein": 18.2, "fat": 2.4, "carbohydrate": 1.4,
     "fiber": 0, "sodium": 165, "sugar": 0,
     "health_rating": "推荐", "health_tips": "肉质紧实，白灼最佳"},

    # ===== 蛋奶类 =====
    {"name": "鸡蛋", "alias": "鸡子,鸡卵", "category": "蛋类",
     "calories": 144, "protein": 13.3, "fat": 8.8, "carbohydrate": 2.8,
     "fiber": 0, "sodium": 131, "sugar": 1.1,
     "health_rating": "推荐", "health_tips": "完美蛋白质来源，每天1-2个"},

    {"name": "鸭蛋", "alias": "鸭子蛋,鸭卵", "category": "蛋类",
     "calories": 180, "protein": 12.6, "fat": 13.0, "carbohydrate": 3.1,
     "fiber": 0, "sodium": 106, "sugar": 1.0,
     "health_rating": "适量", "health_tips": "营养丰富，腌制后更美味"},

    {"name": "牛奶", "alias": "鲜牛奶,纯牛奶", "category": "乳制品",
     "calories": 54, "protein": 3.0, "fat": 3.2, "carbohydrate": 3.4,
     "fiber": 0, "sodium": 37, "sugar": 3.4,
     "health_rating": "推荐", "health_tips": "补钙佳品，乳糖不耐受者慎饮"},

    # ===== 主食类 =====
    {"name": "大米", "alias": "粳米,白米", "category": "主食",
     "calories": 346, "protein": 7.4, "fat": 0.8, "carbohydrate": 77.9,
     "fiber": 0.7, "sodium": 3.8, "sugar": 0.5,
     "health_rating": "适量", "health_tips": "主要能量来源，搭配蔬菜更健康"},

    {"name": "小米", "alias": "粟米,谷子", "category": "主食",
     "calories": 358, "protein": 9.0, "fat": 3.1, "carbohydrate": 75.1,
     "fiber": 1.6, "sodium": 4.3, "sugar": 0.8,
     "health_rating": "推荐", "health_tips": "养胃佳品，适合煮粥"},

    {"name": "燕麦", "alias": "莜麦,雀麦", "category": "主食",
     "calories": 338, "protein": 10.1, "fat": 7.0, "carbohydrate": 61.6,
     "fiber": 5.3, "sodium": 3.7, "sugar": 0.5,
     "health_rating": "推荐", "health_tips": "富含膳食纤维，降血脂佳品"},

    {"name": "玉米", "alias": "苞米,棒子", "category": "主食",
     "calories": 112, "protein": 4.0, "fat": 1.2, "carbohydrate": 22.8,
     "fiber": 2.9, "sodium": 1.1, "sugar": 3.2,
     "health_rating": "推荐", "health_tips": "粗粮代表，富含膳食纤维"},

    {"name": "红豆", "alias": "赤小豆,赤豆", "category": "主食",
     "calories": 309, "protein": 20.2, "fat": 0.6, "carbohydrate": 63.4,
     "fiber": 7.7, "sodium": 2.2, "sugar": 3.2,
     "health_rating": "推荐", "health_tips": "利水消肿，美容养颜"},

    {"name": "绿豆", "alias": "青小豆,植豆", "category": "主食",
     "calories": 316, "protein": 21.6, "fat": 0.8, "carbohydrate": 62.0,
     "fiber": 6.4, "sodium": 3.2, "sugar": 4.1,
     "health_rating": "推荐", "health_tips": "清热解毒，夏季消暑佳品"},
]


def init_chinese_foods(db: Session):
    """初始化中国常见食材数据"""
    added_count = 0
    skipped_count = 0

    for food_data in CHINESE_FOODS:
        # 检查是否已存在
        existing = db.query(Food).filter(Food.name == food_data["name"]).first()
        if existing:
            skipped_count += 1
            continue

        food = Food(
            name=food_data["name"],
            alias=food_data.get("alias"),
            category=food_data["category"],
            calories=food_data["calories"],
            protein=food_data["protein"],
            fat=food_data["fat"],
            carbohydrate=food_data["carbohydrate"],
            fiber=food_data.get("fiber"),
            sodium=food_data.get("sodium"),
            sugar=food_data.get("sugar"),
            health_rating=food_data.get("health_rating", "适量"),
            health_tips=food_data.get("health_tips"),
            source="中国食物成分表",
        )
        db.add(food)
        added_count += 1

    db.commit()
    print(f"  [OK] Chinese foods: added {added_count}, skipped {skipped_count}")
