# -*- coding: utf-8 -*-
"""
精品食谱初始数据
"""
import json
from sqlalchemy.orm import Session

from app.models.food import PremiumRecipe


def init_premium_recipes(db: Session):
    """初始化精品食谱数据"""
    # 检查是否已有数据
    if db.query(PremiumRecipe).count() > 0:
        return
    
    recipes = [
        # 早餐
        PremiumRecipe(
            name="牛油果鸡蛋三明治",
            description="营养丰富的西式早餐，牛油果提供优质脂肪，鸡蛋提供蛋白质",
            category="早餐",
            tags=json.dumps(["高蛋白", "低碳水", "快手早餐"], ensure_ascii=False),
            cook_time="10分钟",
            prep_time="5分钟",
            servings=1,
            difficulty="简单",
            calories=380,
            protein=15.0,
            fat=22.0,
            carbs=28.0,
            fiber=6.0,
            sodium=450,
            ingredients=json.dumps([
                {"name": "全麦面包", "amount": "2片"},
                {"name": "牛油果", "amount": "半个"},
                {"name": "鸡蛋", "amount": "1个"},
                {"name": "黑胡椒", "amount": "少许"},
                {"name": "盐", "amount": "少许"},
            ], ensure_ascii=False),
            steps=json.dumps([
                {"step": 1, "content": "鸡蛋煮熟或煎成太阳蛋"},
                {"step": 2, "content": "牛油果切开，去核，用勺子挖出果肉"},
                {"step": 3, "content": "将牛油果捣成泥，加盐和黑胡椒调味"},
                {"step": 4, "content": "面包烤至微脆，涂上牛油果泥"},
                {"step": 5, "content": "放上鸡蛋，即可享用"},
            ], ensure_ascii=False),
            tips="牛油果要选熟透的，按压有轻微凹陷感最佳",
            suitable_for="上班族、健身人群",
            is_featured=True,
            sort_order=100,
        ),
        
        # 午餐
        PremiumRecipe(
            name="香煎鸡胸肉沙拉",
            description="高蛋白低脂的健康午餐，适合减脂期间食用",
            category="午餐",
            tags=json.dumps(["高蛋白", "低脂", "减脂餐", "沙拉"], ensure_ascii=False),
            cook_time="15分钟",
            prep_time="10分钟",
            servings=1,
            difficulty="简单",
            calories=320,
            protein=35.0,
            fat=12.0,
            carbs=15.0,
            fiber=4.0,
            sodium=380,
            ingredients=json.dumps([
                {"name": "鸡胸肉", "amount": "150g"},
                {"name": "生菜", "amount": "100g"},
                {"name": "小番茄", "amount": "5个"},
                {"name": "黄瓜", "amount": "半根"},
                {"name": "橄榄油", "amount": "1勺"},
                {"name": "柠檬汁", "amount": "少许"},
                {"name": "黑胡椒", "amount": "少许"},
            ], ensure_ascii=False),
            steps=json.dumps([
                {"step": 1, "content": "鸡胸肉用盐、黑胡椒腌制10分钟"},
                {"step": 2, "content": "平底锅加少许橄榄油，中火煎鸡胸肉"},
                {"step": 3, "content": "每面煎4-5分钟至金黄熟透，取出切片"},
                {"step": 4, "content": "蔬菜洗净，生菜撕成小片，黄瓜切片，番茄对切"},
                {"step": 5, "content": "摆盘，淋上橄榄油和柠檬汁"},
            ], ensure_ascii=False),
            tips="鸡胸肉不要煎过头，否则会变柴",
            suitable_for="减脂人群、健身人群",
            is_featured=True,
            sort_order=95,
        ),
        
        # 晚餐
        PremiumRecipe(
            name="清蒸鲈鱼",
            description="经典粤式清蒸鱼，保留鱼肉鲜嫩，是最健康的烹饪方式",
            category="晚餐",
            tags=json.dumps(["低脂", "高蛋白", "清淡", "经典菜"], ensure_ascii=False),
            cook_time="15分钟",
            prep_time="10分钟",
            servings=2,
            difficulty="中等",
            calories=180,
            protein=28.0,
            fat=5.0,
            carbs=2.0,
            fiber=0.5,
            sodium=520,
            ingredients=json.dumps([
                {"name": "鲈鱼", "amount": "1条(约500g)"},
                {"name": "葱", "amount": "2根"},
                {"name": "姜", "amount": "1块"},
                {"name": "蒸鱼豉油", "amount": "2勺"},
                {"name": "料酒", "amount": "1勺"},
                {"name": "食用油", "amount": "2勺"},
            ], ensure_ascii=False),
            steps=json.dumps([
                {"step": 1, "content": "鲈鱼清洗干净，两面划几刀便于入味"},
                {"step": 2, "content": "姜切片，葱切段，放在鱼肚和鱼身"},
                {"step": 3, "content": "淋上料酒，水开后大火蒸8-10分钟"},
                {"step": 4, "content": "取出倒掉蒸出的水，放上葱丝"},
                {"step": 5, "content": "淋上蒸鱼豉油，热油浇在葱丝上即可"},
            ], ensure_ascii=False),
            tips="蒸鱼时间不宜过长，否则肉质会变老",
            suitable_for="老人、儿童、减脂人群",
            is_featured=True,
            sort_order=90,
        ),
        
        # 汤品
        PremiumRecipe(
            name="番茄蛋花汤",
            description="家常汤品，酸甜可口，开胃又营养",
            category="汤品",
            tags=json.dumps(["低卡", "开胃", "家常", "快手"], ensure_ascii=False),
            cook_time="10分钟",
            prep_time="5分钟",
            servings=2,
            difficulty="简单",
            calories=65,
            protein=4.0,
            fat=3.0,
            carbs=6.0,
            fiber=1.0,
            sodium=380,
            ingredients=json.dumps([
                {"name": "番茄", "amount": "2个"},
                {"name": "鸡蛋", "amount": "2个"},
                {"name": "葱花", "amount": "少许"},
                {"name": "盐", "amount": "适量"},
                {"name": "香油", "amount": "几滴"},
            ], ensure_ascii=False),
            steps=json.dumps([
                {"step": 1, "content": "番茄洗净切块，鸡蛋打散"},
                {"step": 2, "content": "锅中放少许油，下番茄翻炒出汁"},
                {"step": 3, "content": "加入清水煮开"},
                {"step": 4, "content": "淋入蛋液，用筷子轻轻搅动形成蛋花"},
                {"step": 5, "content": "加盐调味，撒葱花，滴香油即可"},
            ], ensure_ascii=False),
            tips="蛋液要在水沸腾时淋入，这样蛋花更漂亮",
            suitable_for="全家人",
            is_featured=False,
            sort_order=80,
        ),
        
        # 素食
        PremiumRecipe(
            name="蒜蓉西兰花",
            description="简单快手的减脂蔬菜，西兰花富含维生素C和膳食纤维",
            category="晚餐",
            tags=json.dumps(["素食", "低卡", "快手", "减脂"], ensure_ascii=False),
            cook_time="5分钟",
            prep_time="5分钟",
            servings=2,
            difficulty="简单",
            calories=80,
            protein=4.0,
            fat=4.0,
            carbs=8.0,
            fiber=3.5,
            sodium=280,
            ingredients=json.dumps([
                {"name": "西兰花", "amount": "300g"},
                {"name": "蒜", "amount": "4瓣"},
                {"name": "蚝油", "amount": "1勺"},
                {"name": "盐", "amount": "少许"},
                {"name": "食用油", "amount": "1勺"},
            ], ensure_ascii=False),
            steps=json.dumps([
                {"step": 1, "content": "西兰花切小朵，清水加盐浸泡10分钟"},
                {"step": 2, "content": "水烧开，焯水1分钟捞出沥干"},
                {"step": 3, "content": "蒜切末，锅中油热后爆香蒜末"},
                {"step": 4, "content": "下西兰花翻炒，加蚝油和少许盐"},
                {"step": 5, "content": "翻炒均匀即可出锅"},
            ], ensure_ascii=False),
            tips="焯水时加点油和盐，西兰花颜色更翠绿",
            suitable_for="减脂人群、素食者",
            is_featured=True,
            sort_order=85,
        ),
    ]
    
    db.add_all(recipes)
    print(f"  ✓ 已初始化 {len(recipes)} 条精品食谱数据")
