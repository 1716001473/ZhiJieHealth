# -*- coding: utf-8 -*-
"""
常见单品食物数据 - 早餐/加餐/水果/饮品/零食
补充 init_data.py 和 chinese_foods_data.py 中缺失的日常高频食物
"""
from sqlalchemy.orm import Session
from app.models.food import Food


# 常见单品食物数据（每100g营养成分）
COMMON_FOODS = [
    # ===== 早餐类 =====
    {"name": "包子", "alias": "肉包,菜包,小笼包", "category": "主食",
     "calories": 220, "protein": 7.0, "fat": 5.5, "carbohydrate": 36.0,
     "fiber": 1.2, "sodium": 450, "sugar": 2.0,
     "health_rating": "适量", "health_tips": "方便早餐，注意肉馅脂肪含量"},

    {"name": "油条", "alias": "油炸鬼,果子", "category": "主食",
     "calories": 386, "protein": 6.9, "fat": 17.6, "carbohydrate": 51.0,
     "fiber": 0.9, "sodium": 580, "sugar": 1.0,
     "health_rating": "少食", "health_tips": "油炸食品，偶尔食用，不宜常吃"},

    {"name": "煎饼", "alias": "煎饼果子,杂粮煎饼", "category": "主食",
     "calories": 235, "protein": 8.0, "fat": 8.5, "carbohydrate": 33.0,
     "fiber": 2.0, "sodium": 520, "sugar": 1.5,
     "health_rating": "适量", "health_tips": "杂粮煎饼营养较均衡"},

    {"name": "面包", "alias": "吐司,切片面包,白面包", "category": "主食",
     "calories": 266, "protein": 8.0, "fat": 3.5, "carbohydrate": 50.0,
     "fiber": 2.7, "sodium": 460, "sugar": 5.0,
     "health_rating": "适量", "health_tips": "全麦面包比白面包更健康"},

    {"name": "全麦面包", "alias": "全麦吐司,黑面包", "category": "主食",
     "calories": 247, "protein": 10.0, "fat": 3.0, "carbohydrate": 43.0,
     "fiber": 6.8, "sodium": 400, "sugar": 4.0,
     "health_rating": "推荐", "health_tips": "富含膳食纤维，升糖指数低"},

    {"name": "三明治", "alias": "sandwich,夹心面包", "category": "主食",
     "calories": 250, "protein": 10.0, "fat": 10.0, "carbohydrate": 30.0,
     "fiber": 1.5, "sodium": 550, "sugar": 3.0,
     "health_rating": "适量", "health_tips": "搭配蔬菜和瘦肉更健康"},

    {"name": "粥", "alias": "白粥,大米粥,稀饭", "category": "主食",
     "calories": 46, "protein": 1.1, "fat": 0.3, "carbohydrate": 9.8,
     "fiber": 0.1, "sodium": 3, "sugar": 0.2,
     "health_rating": "推荐", "health_tips": "易消化，养胃佳品"},

    {"name": "小米粥", "alias": "黄米粥,谷子粥", "category": "主食",
     "calories": 46, "protein": 1.4, "fat": 0.7, "carbohydrate": 8.4,
     "fiber": 0.3, "sodium": 2, "sugar": 0.3,
     "health_rating": "推荐", "health_tips": "养胃安神，适合早餐"},

    {"name": "八宝粥", "alias": "腊八粥,杂粮粥", "category": "主食",
     "calories": 58, "protein": 1.5, "fat": 0.3, "carbohydrate": 12.5,
     "fiber": 0.8, "sodium": 15, "sugar": 4.0,
     "health_rating": "适量", "health_tips": "营养丰富，注意含糖量"},

    {"name": "馄饨", "alias": "云吞,抄手,扁食", "category": "主食",
     "calories": 120, "protein": 5.5, "fat": 3.5, "carbohydrate": 17.0,
     "fiber": 0.5, "sodium": 480, "sugar": 0.5,
     "health_rating": "适量", "health_tips": "皮薄馅多，搭配汤更暖胃"},

    {"name": "汤圆", "alias": "元宵,圆子", "category": "主食",
     "calories": 230, "protein": 4.0, "fat": 6.0, "carbohydrate": 40.0,
     "fiber": 0.5, "sodium": 20, "sugar": 15.0,
     "health_rating": "少食", "health_tips": "糯米不易消化，含糖量高"},

    {"name": "粽子", "alias": "肉粽,豆沙粽", "category": "主食",
     "calories": 195, "protein": 5.0, "fat": 4.0, "carbohydrate": 35.0,
     "fiber": 0.8, "sodium": 300, "sugar": 5.0,
     "health_rating": "适量", "health_tips": "糯米制品，不宜多食"},

    {"name": "麦片", "alias": "燕麦片,即食麦片,冲泡麦片", "category": "主食",
     "calories": 367, "protein": 12.0, "fat": 7.0, "carbohydrate": 62.0,
     "fiber": 8.5, "sodium": 5, "sugar": 1.0,
     "health_rating": "推荐", "health_tips": "高纤维早餐，搭配牛奶更营养"},

    {"name": "花卷", "alias": "花卷馒头", "category": "主食",
     "calories": 211, "protein": 6.5, "fat": 2.0, "carbohydrate": 42.0,
     "fiber": 1.0, "sodium": 350, "sugar": 1.5,
     "health_rating": "适量", "health_tips": "传统面食，口感松软"},

    {"name": "烧饼", "alias": "芝麻烧饼,火烧", "category": "主食",
     "calories": 295, "protein": 8.0, "fat": 8.0, "carbohydrate": 48.0,
     "fiber": 1.5, "sodium": 520, "sugar": 2.0,
     "health_rating": "适量", "health_tips": "热量较高，注意食用量"},

    # ===== 水果类（补充现有缺失的） =====
    {"name": "橙子", "alias": "甜橙,脐橙,柳橙", "category": "水果",
     "calories": 47, "protein": 0.9, "fat": 0.1, "carbohydrate": 11.8,
     "fiber": 2.4, "sodium": 0, "sugar": 9.4,
     "health_rating": "推荐", "health_tips": "富含维生素C，增强免疫力"},

    {"name": "草莓", "alias": "洋莓,红莓", "category": "水果",
     "calories": 32, "protein": 0.7, "fat": 0.3, "carbohydrate": 7.7,
     "fiber": 2.0, "sodium": 1, "sugar": 4.9,
     "health_rating": "推荐", "health_tips": "低热量高维C，抗氧化佳品"},

    {"name": "猕猴桃", "alias": "奇异果,藤梨", "category": "水果",
     "calories": 61, "protein": 1.1, "fat": 0.5, "carbohydrate": 14.7,
     "fiber": 3.0, "sodium": 3, "sugar": 9.0,
     "health_rating": "推荐", "health_tips": "维生素C之王，助消化"},

    {"name": "梨", "alias": "雪梨,鸭梨,香梨", "category": "水果",
     "calories": 57, "protein": 0.4, "fat": 0.1, "carbohydrate": 15.2,
     "fiber": 3.1, "sodium": 1, "sugar": 9.8,
     "health_rating": "推荐", "health_tips": "润肺止咳，秋冬佳果"},

    {"name": "桃子", "alias": "水蜜桃,毛桃,蟠桃", "category": "水果",
     "calories": 39, "protein": 0.9, "fat": 0.3, "carbohydrate": 9.5,
     "fiber": 1.5, "sodium": 0, "sugar": 8.4,
     "health_rating": "推荐", "health_tips": "夏季时令水果，鲜甜多汁"},

    {"name": "芒果", "alias": "杧果,望果", "category": "水果",
     "calories": 60, "protein": 0.8, "fat": 0.4, "carbohydrate": 15.0,
     "fiber": 1.6, "sodium": 1, "sugar": 13.7,
     "health_rating": "适量", "health_tips": "含糖较高，过敏体质者慎食"},

    {"name": "蓝莓", "alias": "笃斯越橘", "category": "水果",
     "calories": 57, "protein": 0.7, "fat": 0.3, "carbohydrate": 14.5,
     "fiber": 2.4, "sodium": 1, "sugar": 10.0,
     "health_rating": "推荐", "health_tips": "花青素丰富，护眼抗氧化"},

    {"name": "樱桃", "alias": "车厘子,含桃", "category": "水果",
     "calories": 63, "protein": 1.1, "fat": 0.2, "carbohydrate": 16.0,
     "fiber": 2.1, "sodium": 0, "sugar": 12.8,
     "health_rating": "适量", "health_tips": "补铁佳果，但含糖量较高"},

    {"name": "柚子", "alias": "文旦,香栾,朱栾", "category": "水果",
     "calories": 42, "protein": 0.8, "fat": 0.1, "carbohydrate": 10.7,
     "fiber": 1.0, "sodium": 1, "sugar": 7.0,
     "health_rating": "推荐", "health_tips": "低热量，富含维生素C"},

    {"name": "火龙果", "alias": "红龙果,仙蜜果", "category": "水果",
     "calories": 55, "protein": 1.1, "fat": 0.4, "carbohydrate": 13.0,
     "fiber": 1.9, "sodium": 0, "sugar": 8.0,
     "health_rating": "适量", "health_tips": "富含膳食纤维，促进消化"},

    {"name": "哈密瓜", "alias": "甜瓜,蜜瓜", "category": "水果",
     "calories": 34, "protein": 0.8, "fat": 0.1, "carbohydrate": 8.2,
     "fiber": 0.9, "sodium": 18, "sugar": 7.9,
     "health_rating": "适量", "health_tips": "夏季消暑水果，含糖适中"},

    {"name": "荔枝", "alias": "丹荔,离枝", "category": "水果",
     "calories": 66, "protein": 0.8, "fat": 0.4, "carbohydrate": 16.5,
     "fiber": 1.3, "sodium": 1, "sugar": 15.2,
     "health_rating": "少食", "health_tips": "含糖量高，一次不宜超过10颗"},

    {"name": "柿子", "alias": "朱果,红柿", "category": "水果",
     "calories": 71, "protein": 0.7, "fat": 0.2, "carbohydrate": 18.5,
     "fiber": 3.6, "sodium": 1, "sugar": 12.5,
     "health_rating": "适量", "health_tips": "不宜空腹食用，含鞣酸较多"},

    # ===== 加餐/零食类 =====
    {"name": "核桃", "alias": "胡桃,羌桃", "category": "零食",
     "calories": 654, "protein": 15.2, "fat": 65.2, "carbohydrate": 13.7,
     "fiber": 6.7, "sodium": 2, "sugar": 2.6,
     "health_rating": "适量", "health_tips": "健脑益智，每天3-5个为宜"},

    {"name": "杏仁", "alias": "扁桃仁,巴旦木", "category": "零食",
     "calories": 578, "protein": 21.2, "fat": 49.9, "carbohydrate": 21.7,
     "fiber": 12.5, "sodium": 1, "sugar": 4.4,
     "health_rating": "适量", "health_tips": "富含维生素E，每天一小把"},

    {"name": "腰果", "alias": "鸡腰果,介寿果", "category": "零食",
     "calories": 553, "protein": 18.2, "fat": 43.9, "carbohydrate": 30.2,
     "fiber": 3.3, "sodium": 12, "sugar": 5.9,
     "health_rating": "适量", "health_tips": "口感香脆，注意控制食用量"},

    {"name": "花生", "alias": "落花生,长生果", "category": "零食",
     "calories": 567, "protein": 25.8, "fat": 49.2, "carbohydrate": 16.1,
     "fiber": 8.5, "sodium": 18, "sugar": 4.7,
     "health_rating": "适量", "health_tips": "蛋白质丰富，过敏者禁食"},

    {"name": "葵花籽", "alias": "瓜子,向日葵籽", "category": "零食",
     "calories": 584, "protein": 20.8, "fat": 51.5, "carbohydrate": 20.0,
     "fiber": 8.6, "sodium": 9, "sugar": 2.6,
     "health_rating": "适量", "health_tips": "富含维生素E，注意控量"},

    {"name": "红枣", "alias": "大枣,干枣", "category": "零食",
     "calories": 264, "protein": 3.3, "fat": 0.5, "carbohydrate": 67.8,
     "fiber": 6.7, "sodium": 6, "sugar": 30.0,
     "health_rating": "适量", "health_tips": "补血养颜，但含糖量高"},

    {"name": "饼干", "alias": "苏打饼干,消化饼", "category": "零食",
     "calories": 435, "protein": 7.0, "fat": 14.0, "carbohydrate": 71.0,
     "fiber": 2.0, "sodium": 580, "sugar": 15.0,
     "health_rating": "少食", "health_tips": "高糖高脂，偶尔食用"},

    {"name": "巧克力", "alias": "朱古力,黑巧克力", "category": "零食",
     "calories": 546, "protein": 5.0, "fat": 31.0, "carbohydrate": 60.0,
     "fiber": 7.0, "sodium": 24, "sugar": 48.0,
     "health_rating": "少食", "health_tips": "高热量，黑巧克力相对更健康"},

    {"name": "蛋糕", "alias": "奶油蛋糕,海绵蛋糕", "category": "零食",
     "calories": 348, "protein": 5.0, "fat": 15.0, "carbohydrate": 50.0,
     "fiber": 0.5, "sodium": 280, "sugar": 25.0,
     "health_rating": "少食", "health_tips": "高糖高脂，减肥期间避免"},

    {"name": "奶酪", "alias": "芝士,干酪,cheese", "category": "乳制品",
     "calories": 328, "protein": 20.0, "fat": 26.0, "carbohydrate": 3.5,
     "fiber": 0, "sodium": 620, "sugar": 0.5,
     "health_rating": "适量", "health_tips": "高蛋白高钙，但脂肪和钠较高"},

    {"name": "酸奶杯", "alias": "希腊酸奶,浓稠酸奶", "category": "乳制品",
     "calories": 97, "protein": 9.0, "fat": 5.0, "carbohydrate": 3.6,
     "fiber": 0, "sodium": 36, "sugar": 3.2,
     "health_rating": "推荐", "health_tips": "高蛋白低糖，健身加餐首选"},

    # ===== 饮品类 =====
    {"name": "咖啡", "alias": "黑咖啡,美式咖啡", "category": "饮品",
     "calories": 2, "protein": 0.1, "fat": 0, "carbohydrate": 0.4,
     "fiber": 0, "sodium": 2, "sugar": 0,
     "health_rating": "适量", "health_tips": "提神醒脑，不加糖更健康"},

    {"name": "拿铁", "alias": "拿铁咖啡,牛奶咖啡", "category": "饮品",
     "calories": 56, "protein": 3.0, "fat": 2.5, "carbohydrate": 5.5,
     "fiber": 0, "sodium": 50, "sugar": 5.0,
     "health_rating": "适量", "health_tips": "含牛奶补钙，注意含糖量"},

    {"name": "奶茶", "alias": "珍珠奶茶,波霸奶茶", "category": "饮品",
     "calories": 80, "protein": 1.0, "fat": 3.0, "carbohydrate": 12.0,
     "fiber": 0, "sodium": 30, "sugar": 10.0,
     "health_rating": "少食", "health_tips": "高糖高脂，一杯约400-600大卡"},

    {"name": "绿茶", "alias": "茶,清茶", "category": "饮品",
     "calories": 1, "protein": 0.2, "fat": 0, "carbohydrate": 0.3,
     "fiber": 0, "sodium": 1, "sugar": 0,
     "health_rating": "推荐", "health_tips": "抗氧化，提神，零热量"},

    {"name": "橙汁", "alias": "鲜榨橙汁,果汁", "category": "饮品",
     "calories": 45, "protein": 0.7, "fat": 0.2, "carbohydrate": 10.4,
     "fiber": 0.2, "sodium": 1, "sugar": 8.4,
     "health_rating": "适量", "health_tips": "鲜榨更好，注意含糖量"},

    {"name": "可乐", "alias": "碳酸饮料,汽水", "category": "饮品",
     "calories": 42, "protein": 0, "fat": 0, "carbohydrate": 10.6,
     "fiber": 0, "sodium": 4, "sugar": 10.6,
     "health_rating": "少食", "health_tips": "纯糖饮料，尽量少喝"},

    {"name": "蜂蜜水", "alias": "蜂蜜,蜜糖水", "category": "饮品",
     "calories": 15, "protein": 0, "fat": 0, "carbohydrate": 4.0,
     "fiber": 0, "sodium": 1, "sugar": 3.8,
     "health_rating": "适量", "health_tips": "润肠通便，但本质是糖水"},

    # ===== 其他常见单品 =====
    {"name": "茶叶蛋", "alias": "卤蛋,五香蛋", "category": "蛋类",
     "calories": 155, "protein": 13.0, "fat": 10.0, "carbohydrate": 2.5,
     "fiber": 0, "sodium": 450, "sugar": 1.0,
     "health_rating": "适量", "health_tips": "便利早餐，钠含量偏高"},

    {"name": "豆腐脑", "alias": "豆花,豆腐花", "category": "豆制品",
     "calories": 15, "protein": 1.8, "fat": 0.5, "carbohydrate": 0.8,
     "fiber": 0.1, "sodium": 5, "sugar": 0.3,
     "health_rating": "推荐", "health_tips": "低热量高蛋白，早餐佳品"},

    {"name": "肠粉", "alias": "拉肠,布拉肠", "category": "主食",
     "calories": 110, "protein": 3.5, "fat": 2.5, "carbohydrate": 18.0,
     "fiber": 0.3, "sodium": 350, "sugar": 0.5,
     "health_rating": "适量", "health_tips": "广式早餐，口感滑嫩"},

    {"name": "年糕", "alias": "糍粑,水磨年糕", "category": "主食",
     "calories": 190, "protein": 4.0, "fat": 0.3, "carbohydrate": 43.0,
     "fiber": 0.5, "sodium": 10, "sugar": 2.0,
     "health_rating": "适量", "health_tips": "糯米制品，不易消化"},

    {"name": "牛肉干", "alias": "牛肉脯,风干牛肉", "category": "零食",
     "calories": 250, "protein": 45.6, "fat": 4.0, "carbohydrate": 10.0,
     "fiber": 0, "sodium": 1200, "sugar": 3.0,
     "health_rating": "适量", "health_tips": "高蛋白零食，但钠含量很高"},

    {"name": "海苔", "alias": "紫菜片,烤海苔", "category": "零食",
     "calories": 177, "protein": 30.0, "fat": 3.0, "carbohydrate": 20.0,
     "fiber": 3.5, "sodium": 1800, "sugar": 1.0,
     "health_rating": "适量", "health_tips": "富含碘和蛋白质，注意钠含量"},
]


def init_common_foods(db: Session):
    """初始化常见单品食物数据"""
    added_count = 0
    skipped_count = 0

    for food_data in COMMON_FOODS:
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
            source="人工整理",
        )
        db.add(food)
        added_count += 1

    db.commit()
    print(f"  [OK] Common foods: added {added_count}, skipped {skipped_count}")
