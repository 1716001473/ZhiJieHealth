# -*- coding: utf-8 -*-
"""
数据库初始化数据
包含烹饪方式、份量选项、禁忌规则和常见食物数据
"""
from sqlalchemy.orm import Session

from app.models.food import Food, FoodContraindication, FoodPortion, CookingMethod


def init_cooking_methods(db: Session):
    """初始化烹饪方式数据"""
    # 检查是否已有数据
    if db.query(CookingMethod).count() > 0:
        return
    
    methods = [
        CookingMethod(name="清蒸", calorie_adjust=-20, calorie_percent=-10, 
                     description="保留原味，几乎不加油", icon="steam", sort_order=1),
        CookingMethod(name="水煮", calorie_adjust=-10, calorie_percent=-5, 
                     description="少油少盐，相对健康", icon="boil", sort_order=2),
        CookingMethod(name="少油炒", calorie_adjust=0, calorie_percent=0, 
                     description="正常烹饪，作为基准", icon="stir-fry", sort_order=3),
        CookingMethod(name="红烧", calorie_adjust=50, calorie_percent=20, 
                     description="加糖加油，热量增加", icon="braise", sort_order=4),
        CookingMethod(name="油炸", calorie_adjust=150, calorie_percent=50, 
                     description="大量用油，热量大增", icon="fry", sort_order=5),
    ]
    db.add_all(methods)
    print("  ✓ 烹饪方式数据已初始化")


def init_portions(db: Session):
    """初始化通用份量选项"""
    # 检查是否已有数据
    if db.query(FoodPortion).count() > 0:
        return
    
    portions = [
        FoodPortion(portion_name="小份", weight_grams=120, calorie_factor=0.6, 
                   is_default=False, sort_order=1),
        FoodPortion(portion_name="中份", weight_grams=200, calorie_factor=1.0, 
                   is_default=True, sort_order=2),
        FoodPortion(portion_name="大份", weight_grams=300, calorie_factor=1.5, 
                   is_default=False, sort_order=3),
    ]
    db.add_all(portions)
    print("  ✓ 份量选项数据已初始化")


def init_contraindications(db: Session):
    """初始化通用禁忌规则"""
    # 检查是否已有数据
    if db.query(FoodContraindication).count() > 0:
        return
    
    rules = [
        # 糖尿病相关
        FoodContraindication(food_keyword="糖", condition_type="糖尿病", severity="慎食",
                            reason="含糖量高，可能导致血糖快速升高", suggestion="建议选择低GI食物"),
        FoodContraindication(food_keyword="甜", condition_type="糖尿病", severity="少食",
                            reason="甜味食品通常含糖较多", suggestion="可选择无糖或代糖食品"),
        FoodContraindication(food_keyword="蛋糕", condition_type="糖尿病", severity="慎食",
                            reason="高糖高脂，血糖影响大", suggestion="建议选择无糖糕点"),
        
        # 高血脂相关
        FoodContraindication(food_keyword="油炸", condition_type="高血脂", severity="少食",
                            reason="油炸食品脂肪含量高", suggestion="建议清蒸或水煮"),
        FoodContraindication(food_keyword="肥肉", condition_type="高血脂", severity="慎食",
                            reason="饱和脂肪含量高", suggestion="建议选择瘦肉"),
        FoodContraindication(food_keyword="红烧肉", condition_type="高血脂", severity="少食",
                            reason="脂肪含量较高", suggestion="建议适量食用"),
        
        # 痛风相关
        FoodContraindication(food_keyword="海鲜", condition_type="痛风", severity="慎食",
                            reason="海鲜嘌呤含量较高", suggestion="急性发作期应禁食"),
        FoodContraindication(food_keyword="虾", condition_type="痛风", severity="慎食",
                            reason="虾类嘌呤含量中等偏高", suggestion="缓解期可少量食用"),
        FoodContraindication(food_keyword="蟹", condition_type="痛风", severity="慎食",
                            reason="蟹类嘌呤含量较高", suggestion="建议避免食用"),
        FoodContraindication(food_keyword="内脏", condition_type="痛风", severity="禁食",
                            reason="动物内脏嘌呤含量极高", suggestion="痛风患者应严格禁食"),
        
        # 高血压相关
        FoodContraindication(food_keyword="腌制", condition_type="高血压", severity="少食",
                            reason="钠含量高", suggestion="建议选择新鲜食材"),
        FoodContraindication(food_keyword="咸", condition_type="高血压", severity="少食",
                            reason="高盐饮食不利于血压控制", suggestion="建议清淡饮食"),
        FoodContraindication(food_keyword="酱", condition_type="高血压", severity="少食",
                            reason="酱类食品钠含量通常较高", suggestion="建议减少用量"),
        
        # 过敏体质相关
        FoodContraindication(food_keyword="海鲜", condition_type="过敏体质", severity="慎食",
                            reason="常见过敏原", suggestion="首次食用请少量尝试"),
        FoodContraindication(food_keyword="花生", condition_type="过敏体质", severity="慎食",
                            reason="常见坚果过敏原", suggestion="过敏者应严格避免"),
        FoodContraindication(food_keyword="牛奶", condition_type="乳糖不耐受", severity="慎食",
                            reason="含乳糖，可能引起不适", suggestion="可选择无乳糖或植物奶"),
        
        # 孕妇相关
        FoodContraindication(food_keyword="生冷", condition_type="孕妇", severity="慎食",
                            reason="可能存在细菌污染风险", suggestion="建议食用熟食"),
        FoodContraindication(food_keyword="生鱼片", condition_type="孕妇", severity="禁食",
                            reason="可能含有寄生虫", suggestion="孕期应避免生食"),
        FoodContraindication(food_keyword="酒", condition_type="孕妇", severity="禁食",
                            reason="酒精影响胎儿发育", suggestion="孕期应严格禁酒"),
        
        # 胃病相关
        FoodContraindication(food_keyword="辛辣", condition_type="胃病", severity="少食",
                            reason="刺激胃黏膜", suggestion="建议清淡饮食"),
        FoodContraindication(food_keyword="油腻", condition_type="胃病", severity="少食",
                            reason="不易消化，加重胃负担", suggestion="建议清淡少油"),
        FoodContraindication(food_keyword="酸", condition_type="胃病", severity="少食",
                            reason="可能刺激胃酸分泌", suggestion="胃酸过多者应注意"),
    ]
    db.add_all(rules)
    print("  ✓ 禁忌规则数据已初始化")


def init_foods(db: Session):
    """初始化常见食物数据"""
    # 检查是否已有数据
    if db.query(Food).count() > 0:
        return
    
    foods = [
        # ===== 荤菜 =====
        Food(name="宫保鸡丁", category="荤菜", calories=180, protein=15.2, fat=10.5, 
             carbohydrate=8.3, fiber=1.5, sodium=680, sugar=3.2,
             serving_desc="一盘约200g", serving_weight=200, health_rating="适量",
             health_tips="蛋白质丰富，但油脂和钠含量较高，建议适量食用"),
        
        Food(name="鱼香肉丝", category="荤菜", calories=165, protein=12.8, fat=9.2, 
             carbohydrate=10.5, fiber=2.0, sodium=720, sugar=4.5,
             serving_desc="一盘约200g", serving_weight=200, health_rating="适量",
             health_tips="含有多种蔬菜，营养较均衡，但糖和钠偏高"),
        
        Food(name="红烧肉", category="荤菜", calories=320, protein=14.5, fat=28.0, 
             carbohydrate=6.0, fiber=0.2, sodium=850, sugar=5.0,
             serving_desc="一份约150g", serving_weight=150, health_rating="少食",
             health_tips="脂肪含量高，高血脂、肥胖者应少食"),
        
        Food(name="糖醋里脊", category="荤菜", calories=245, protein=13.0, fat=12.5, 
             carbohydrate=20.0, fiber=0.5, sodium=580, sugar=15.0,
             serving_desc="一盘约180g", serving_weight=180, health_rating="少食",
             health_tips="糖分较高，糖尿病患者应谨慎食用"),
        
        Food(name="清蒸鱼", category="荤菜", calories=95, protein=18.5, fat=2.0, 
             carbohydrate=0.5, fiber=0, sodium=380, sugar=0,
             serving_desc="一条约300g", serving_weight=300, health_rating="推荐",
             health_tips="高蛋白低脂肪，非常健康的选择"),
        
        Food(name="水煮牛肉", category="荤菜", calories=155, protein=20.0, fat=7.5, 
             carbohydrate=3.0, fiber=1.5, sodium=920, sugar=1.0,
             serving_desc="一份约250g", serving_weight=250, health_rating="适量",
             health_tips="蛋白质丰富，但辣椒油较多，钠含量高"),
        
        Food(name="回锅肉", category="荤菜", calories=285, protein=12.0, fat=24.0, 
             carbohydrate=6.5, fiber=1.0, sodium=780, sugar=2.0,
             serving_desc="一盘约200g", serving_weight=200, health_rating="少食",
             health_tips="脂肪含量较高，建议少量食用"),
        
        Food(name="番茄炒蛋", category="荤菜", calories=92, protein=6.5, fat=5.8, 
             carbohydrate=5.0, fiber=0.8, sodium=420, sugar=3.5,
             serving_desc="一盘约200g", serving_weight=200, health_rating="推荐",
             health_tips="营养均衡，老少皆宜的家常菜"),
        
        Food(name="青椒肉丝", category="荤菜", calories=125, protein=11.5, fat=7.0, 
             carbohydrate=5.5, fiber=1.8, sodium=520, sugar=2.0,
             serving_desc="一盘约200g", serving_weight=200, health_rating="推荐",
             health_tips="蔬菜肉类搭配合理，是健康的选择"),
        
        Food(name="可乐鸡翅", category="荤菜", calories=195, protein=16.0, fat=11.0, 
             carbohydrate=9.5, fiber=0, sodium=650, sugar=8.0,
             serving_desc="6个约200g", serving_weight=200, health_rating="少食",
             health_tips="含糖量较高，不宜多食"),
        
        # ===== 素菜 =====
        Food(name="清炒西兰花", category="素菜", calories=45, protein=3.5, fat=2.0, 
             carbohydrate=4.5, fiber=2.5, sodium=280, sugar=1.5,
             serving_desc="一盘约200g", serving_weight=200, health_rating="推荐",
             health_tips="富含维生素C和膳食纤维，非常健康"),
        
        Food(name="蒜蓉菠菜", category="素菜", calories=55, protein=2.8, fat=3.0, 
             carbohydrate=4.0, fiber=2.2, sodium=350, sugar=0.5,
             serving_desc="一盘约200g", serving_weight=200, health_rating="推荐",
             health_tips="富含铁和维生素，建议连汤一起食用"),
        
        Food(name="地三鲜", category="素菜", calories=135, protein=2.5, fat=10.0, 
             carbohydrate=10.0, fiber=2.0, sodium=420, sugar=3.0,
             serving_desc="一盘约250g", serving_weight=250, health_rating="适量",
             health_tips="茄子、土豆、青椒吸油较多，热量偏高"),
        
        Food(name="醋溜白菜", category="素菜", calories=35, protein=1.5, fat=1.5, 
             carbohydrate=4.5, fiber=1.0, sodium=320, sugar=2.0,
             serving_desc="一盘约200g", serving_weight=200, health_rating="推荐",
             health_tips="低热量蔬菜，减肥期间的好选择"),
        
        Food(name="麻婆豆腐", category="素菜", calories=120, protein=8.0, fat=8.0, 
             carbohydrate=5.0, fiber=0.5, sodium=680, sugar=1.5,
             serving_desc="一盘约200g", serving_weight=200, health_rating="适量",
             health_tips="豆腐富含蛋白质，但辣椒油较多"),
        
        # ===== 主食 =====
        Food(name="白米饭", category="主食", calories=116, protein=2.6, fat=0.3, 
             carbohydrate=25.6, fiber=0.3, sodium=2, sugar=0,
             serving_desc="一碗约150g", serving_weight=150, health_rating="适量",
             health_tips="主要提供碳水化合物，建议搭配蔬菜肉类"),
        
        Food(name="馒头", category="主食", calories=223, protein=7.0, fat=1.1, 
             carbohydrate=45.7, fiber=1.3, sodium=230, sugar=1.5,
             serving_desc="一个约80g", serving_weight=80, health_rating="适量",
             health_tips="北方传统主食，碳水含量高"),
        
        Food(name="面条", category="主食", calories=110, protein=3.5, fat=0.5, 
             carbohydrate=23.0, fiber=0.8, sodium=150, sugar=0.5,
             serving_desc="一碗约200g（煮后）", serving_weight=200, health_rating="适量",
             health_tips="易消化的主食，可搭配各种配菜"),
        
        Food(name="饺子", category="主食", calories=185, protein=7.5, fat=8.0, 
             carbohydrate=22.0, fiber=1.0, sodium=450, sugar=1.0,
             serving_desc="10个约200g", serving_weight=200, health_rating="适量",
             health_tips="荤素搭配的完整餐食，注意肉馅脂肪含量"),
        
        Food(name="炒饭", category="主食", calories=175, protein=5.0, fat=7.0, 
             carbohydrate=23.0, fiber=0.8, sodium=580, sugar=0.5,
             serving_desc="一盘约300g", serving_weight=300, health_rating="适量",
             health_tips="油盐较多，建议少放油"),
        
        # ===== 汤类 =====
        Food(name="番茄蛋汤", category="汤类", calories=32, protein=2.5, fat=1.5, 
             carbohydrate=2.5, fiber=0.5, sodium=380, sugar=2.0,
             serving_desc="一碗约250ml", serving_weight=250, health_rating="推荐",
             health_tips="低热量汤品，开胃又营养"),
        
        Food(name="紫菜蛋花汤", category="汤类", calories=28, protein=2.8, fat=1.2, 
             carbohydrate=2.0, fiber=0.8, sodium=420, sugar=0.5,
             serving_desc="一碗约250ml", serving_weight=250, health_rating="推荐",
             health_tips="富含碘元素，适合日常食用"),
        
        Food(name="排骨汤", category="汤类", calories=65, protein=5.0, fat=4.5, 
             carbohydrate=1.5, fiber=0, sodium=280, sugar=0,
             serving_desc="一碗约300ml", serving_weight=300, health_rating="适量",
             health_tips="补钙佳品，但骨汤脂肪较多"),
        
        # ===== 水果 =====
        Food(name="苹果", category="水果", calories=52, protein=0.3, fat=0.2, 
             carbohydrate=13.8, fiber=2.4, sodium=1, sugar=10.4,
             serving_desc="一个约200g", serving_weight=200, health_rating="推荐",
             health_tips="富含膳食纤维和维生素C，每天一个很健康"),
        
        Food(name="香蕉", category="水果", calories=89, protein=1.1, fat=0.3, 
             carbohydrate=22.8, fiber=2.6, sodium=1, sugar=12.2,
             serving_desc="一根约120g", serving_weight=120, health_rating="适量",
             health_tips="富含钾元素，运动后补充能量的好选择"),
        
        Food(name="西瓜", category="水果", calories=30, protein=0.6, fat=0.1, 
             carbohydrate=7.6, fiber=0.4, sodium=1, sugar=6.2,
             serving_desc="一块约200g", serving_weight=200, health_rating="适量",
             health_tips="水分充足，夏季消暑佳品，糖尿病患者注意用量"),
        
        Food(name="葡萄", category="水果", calories=67, protein=0.7, fat=0.2, 
             carbohydrate=17.2, fiber=0.9, sodium=2, sugar=16.0,
             serving_desc="一小串约150g", serving_weight=150, health_rating="适量",
             health_tips="含糖量较高，注意适量食用"),
        
        # ===== 饮品/零食 =====
        Food(name="豆浆", category="饮品", calories=35, protein=3.0, fat=1.6, 
             carbohydrate=2.5, fiber=0.5, sodium=15, sugar=0,
             serving_desc="一杯约300ml", serving_weight=300, health_rating="推荐",
             health_tips="植物蛋白来源，建议选择无糖或少糖"),
        
        Food(name="酸奶", category="饮品", calories=72, protein=3.5, fat=3.0, 
             carbohydrate=7.0, fiber=0, sodium=50, sugar=5.5,
             serving_desc="一杯约200g", serving_weight=200, health_rating="推荐",
             health_tips="含益生菌，有助于肠道健康"),
        
        Food(name="薯片", category="零食", calories=536, protein=5.0, fat=35.0, 
             carbohydrate=52.0, fiber=3.5, sodium=580, sugar=0.5,
             serving_desc="一包约50g", serving_weight=50, health_rating="少食",
             health_tips="高油高盐，偶尔解馋可以，不宜常吃"),
    ]
    
    db.add_all(foods)
    print(f"  ✓ 已初始化 {len(foods)} 条食物数据")


def init_all_data(db: Session):
    """初始化所有数据"""
    from app.database.chinese_foods_data import init_chinese_foods

    print("📦 正在初始化数据库...")
    init_cooking_methods(db)
    init_portions(db)
    init_contraindications(db)
    init_foods(db)
    init_chinese_foods(db)  # 中国常见食材数据
    print("📦 数据库初始化完成")
