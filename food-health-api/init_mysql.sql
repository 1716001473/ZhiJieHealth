-- =====================================================
-- 智能食物识别健康助手 - MySQL 数据库初始化脚本
-- 版本：v2.0 (2026-02-13)
-- 说明：完全对齐 SQLAlchemy Models，覆盖所有表和字段
-- 用法：mysql -u root -p < init_mysql.sql
-- =====================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS food_health DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE food_health;

-- =====================================================
-- 1. 用户表
-- =====================================================
CREATE TABLE IF NOT EXISTS `user` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(200) NOT NULL COMMENT '密码哈希',
    nickname VARCHAR(100) COMMENT '昵称',
    avatar_url VARCHAR(500) COMMENT '头像URL',

    -- 健康档案基础数据
    weight FLOAT COMMENT '体重(kg)',
    height FLOAT COMMENT '身高(cm)',
    age INT COMMENT '年龄',
    gender VARCHAR(10) COMMENT '性别: male/female',
    activity VARCHAR(20) COMMENT '活动水平: low/medium/high',

    -- 健康档案（逗号分隔字符串）
    health_conditions TEXT COMMENT '健康状况，如"糖尿病,高血压"',
    allergies TEXT COMMENT '过敏原，如"花生,海鲜"',

    -- 个性化目标与偏好
    health_goal VARCHAR(50) DEFAULT 'maintain' COMMENT '健康目标：lose_weight/gain_muscle/maintain',
    dietary_preferences TEXT COMMENT '饮食偏好（逗号分隔）：vegetarian,no_spicy,low_sugar',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';


-- =====================================================
-- 2. 食物表（主表，已审核的正式数据）
-- =====================================================
CREATE TABLE IF NOT EXISTS `food` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '菜品名称',
    alias VARCHAR(200) COMMENT '别名，逗号分隔',
    category VARCHAR(50) COMMENT '分类：主食/荤菜/素菜/汤类/饮品/水果/零食',

    -- 营养数据（每100g）
    calories FLOAT COMMENT '热量 kcal',
    protein FLOAT COMMENT '蛋白质 g',
    fat FLOAT COMMENT '脂肪 g',
    carbohydrate FLOAT COMMENT '碳水化合物 g',
    fiber FLOAT COMMENT '膳食纤维 g',
    sodium FLOAT COMMENT '钠 mg',
    sugar FLOAT COMMENT '糖 g',

    -- 份量参考
    serving_desc VARCHAR(100) COMMENT '常规份量描述',
    serving_weight INT DEFAULT 100 COMMENT '常规份量重量 g',

    -- 健康评级
    health_rating VARCHAR(20) DEFAULT '适量' COMMENT '健康评级：推荐/适量/少食',
    health_tips TEXT COMMENT '健康提示/食用建议',

    -- 元数据
    image_url VARCHAR(500) COMMENT '示例图片URL',
    source VARCHAR(100) COMMENT '数据来源',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_food_name (name),
    INDEX idx_food_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食物主表';


-- =====================================================
-- 3. 临时食物表（AI/用户补充的待校验数据）
-- =====================================================
CREATE TABLE IF NOT EXISTS `food_temp` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '食物名称',

    calories FLOAT NOT NULL COMMENT '热量 kcal/100g',
    protein FLOAT NOT NULL COMMENT '蛋白质 g/100g',
    fat FLOAT NOT NULL COMMENT '脂肪 g/100g',
    carbohydrate FLOAT NOT NULL COMMENT '碳水化合物 g/100g',

    source VARCHAR(50) COMMENT '数据来源：deepseek_ai/baidu_ai/user_custom',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_food_temp_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='临时食物表（AI或用户补充）';


-- =====================================================
-- 4. 食物禁忌表（不适宜人群）
-- =====================================================
CREATE TABLE IF NOT EXISTS `food_contraindication` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT COMMENT '关联食物ID',
    food_keyword VARCHAR(100) COMMENT '食物关键词，用于模糊匹配',

    condition_type VARCHAR(50) NOT NULL COMMENT '疾病/人群类型：糖尿病/高血压/痛风/高血脂/肾病/孕妇等',
    severity VARCHAR(20) NOT NULL DEFAULT '慎食' COMMENT '严重程度：禁食/慎食/少食',
    reason TEXT COMMENT '原因说明',
    suggestion TEXT COMMENT '替代建议',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    FOREIGN KEY (food_id) REFERENCES food(id) ON DELETE CASCADE,
    INDEX idx_contraindication_condition (condition_type),
    INDEX idx_contraindication_food (food_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食物禁忌规则表';


-- =====================================================
-- 5. 食物份量选项表
-- =====================================================
CREATE TABLE IF NOT EXISTS `food_portion` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT COMMENT '关联食物ID',
    category VARCHAR(50) COMMENT '或关联分类',

    portion_name VARCHAR(50) NOT NULL COMMENT '份量名称：小份/中份/大份',
    weight_grams INT COMMENT '对应重量 g',
    calorie_factor FLOAT DEFAULT 1.0 COMMENT '热量系数',

    is_default TINYINT(1) DEFAULT 0 COMMENT '是否默认选项',
    sort_order INT DEFAULT 0 COMMENT '排序顺序',

    FOREIGN KEY (food_id) REFERENCES food(id) ON DELETE CASCADE,
    INDEX idx_portion_food (food_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食物份量选项表';


-- =====================================================
-- 6. 烹饪方式表
-- =====================================================
CREATE TABLE IF NOT EXISTS `cooking_method` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '烹饪方式名称',
    calorie_adjust INT DEFAULT 0 COMMENT '热量调整值 kcal',
    calorie_percent FLOAT DEFAULT 0 COMMENT '热量调整百分比',
    description VARCHAR(200) COMMENT '说明',
    icon VARCHAR(50) COMMENT '图标名称',
    sort_order INT DEFAULT 0 COMMENT '排序顺序'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='烹饪方式表';


-- =====================================================
-- 7. 识别历史表
-- =====================================================
CREATE TABLE IF NOT EXISTS `recognition_history` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',

    -- 识别信息
    image_url VARCHAR(500) COMMENT '原始图片地址',
    recognized_food VARCHAR(100) NOT NULL COMMENT '识别结果（菜品名称）',
    confidence FLOAT COMMENT '置信度 0-1',
    alternatives TEXT COMMENT '其他候选结果 JSON',

    -- 用户确认的参数
    selected_portion VARCHAR(50) COMMENT '用户选择的份量',
    selected_cooking VARCHAR(50) COMMENT '用户选择的烹饪方式',

    -- 计算结果
    final_calories_min INT COMMENT '估算热量下限',
    final_calories_max INT COMMENT '估算热量上限',

    -- 完整识别结果缓存
    result_data LONGTEXT COMMENT '完整识别结果JSON（含营养数据、健康建议）',

    -- 元数据
    meal_type VARCHAR(20) COMMENT '餐次：早餐/午餐/晚餐/加餐',
    note TEXT COMMENT '用户备注',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_history_user (user_id),
    INDEX idx_history_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='识别历史表';


-- =====================================================
-- 8. 饮食记录表（优化版，含营养快照）
-- =====================================================
CREATE TABLE IF NOT EXISTS `meal_record` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    food_id INT COMMENT '关联食物ID，自定义食物可为空',

    -- 快照字段（记录当时的食物信息）
    food_name VARCHAR(100) NOT NULL COMMENT '食物名称快照',
    image_url VARCHAR(500) COMMENT '食物图片URL快照',
    per_100g_calories FLOAT NOT NULL COMMENT '每100g热量(kcal)快照',
    per_100g_protein FLOAT NOT NULL COMMENT '每100g蛋白质(g)快照',
    per_100g_fat FLOAT NOT NULL COMMENT '每100g脂肪(g)快照',
    per_100g_carb FLOAT NOT NULL COMMENT '每100g碳水(g)快照',

    -- 实际摄入量及计算得到的营养值
    meal_date DATE NOT NULL COMMENT '记录日期',
    meal_type ENUM('breakfast','lunch','dinner','snack') NOT NULL COMMENT '餐次类型',
    unit_weight FLOAT NOT NULL COMMENT '摄入重量（克）',
    calories FLOAT NOT NULL COMMENT '摄入热量(kcal)',
    protein FLOAT NOT NULL COMMENT '摄入蛋白质(g)',
    fat FLOAT NOT NULL COMMENT '摄入脂肪(g)',
    carb FLOAT NOT NULL COMMENT '摄入碳水(g)',

    data_source ENUM('database','deepseek_ai','baidu_ai','user_custom','openfoodfacts') NOT NULL DEFAULT 'database' COMMENT '营养数据来源',
    note TEXT COMMENT '用户备注',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_meal_user_date (user_id, meal_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='饮食记录表';


-- =====================================================
-- 9. 体重记录表
-- =====================================================
CREATE TABLE IF NOT EXISTS `weight_record` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    weight FLOAT NOT NULL COMMENT '体重(kg)',
    record_date DATE NOT NULL COMMENT '记录日期',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    INDEX idx_weight_user_date (user_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='体重记录表';


-- =====================================================
-- 10. 食谱计划表
-- =====================================================
CREATE TABLE IF NOT EXISTS `diet_plan` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '食谱名称',
    description TEXT COMMENT '食谱简介',
    cover_image VARCHAR(500) COMMENT '封面图URL',

    -- 基本属性
    duration_days INT DEFAULT 7 COMMENT '持续天数',
    target_user VARCHAR(200) COMMENT '适用人群描述',
    difficulty VARCHAR(20) DEFAULT 'medium' COMMENT '难度: easy/medium/hard',

    -- 增强属性
    tags VARCHAR(500) COMMENT '标签（逗号分隔）：低卡,增肌,素食',
    source VARCHAR(20) DEFAULT 'preset' COMMENT '来源：preset/ai_generated/user_custom',
    author_id INT COMMENT '作者ID',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_plan_source (source)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食谱计划表';


-- =====================================================
-- 11. 食谱计划日表
-- =====================================================
CREATE TABLE IF NOT EXISTS `diet_plan_day` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL COMMENT '所属计划ID',
    day_index INT NOT NULL COMMENT '第几天 (1-21)',
    title VARCHAR(100) COMMENT '当日主题（如：排毒日）',

    -- 目标营养
    total_calories INT COMMENT '总热量 kcal',
    carb_ratio INT COMMENT '碳水比例 %',
    protein_ratio INT COMMENT '蛋白质比例 %',
    fat_ratio INT COMMENT '脂肪比例 %',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

    FOREIGN KEY (plan_id) REFERENCES diet_plan(id) ON DELETE CASCADE,
    INDEX idx_planday_plan (plan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食谱每日安排表';


-- =====================================================
-- 12. 食谱计划餐次表
-- =====================================================
CREATE TABLE IF NOT EXISTS `diet_plan_meal` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day_id INT NOT NULL COMMENT '所属计划日ID',
    meal_type VARCHAR(20) COMMENT '餐次：breakfast/lunch/dinner/snack',
    sort_order INT DEFAULT 0 COMMENT '排序',

    food_name VARCHAR(100) NOT NULL COMMENT '食物名称',
    amount_desc VARCHAR(50) COMMENT '份量描述（如：1个，200g）',
    calories INT DEFAULT 0 COMMENT '估算热量',
    alternatives TEXT COMMENT '替换方案JSON',

    FOREIGN KEY (day_id) REFERENCES diet_plan_day(id) ON DELETE CASCADE,
    INDEX idx_planmeal_day (day_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='食谱具体餐单表';


-- =====================================================
-- 13. 精品食谱表（高质量人工审核内容）
-- =====================================================
CREATE TABLE IF NOT EXISTS `premium_recipes` (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- 基础信息
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '食谱名称',
    description TEXT COMMENT '食谱简介/描述',
    image_url VARCHAR(500) COMMENT '主图URL（AI生成的精美配图）',

    -- 分类与标签
    category VARCHAR(50) COMMENT '主分类：早餐/午餐/晚餐/加餐/汤品/甜点',
    tags TEXT COMMENT '标签JSON数组，如["低脂","高蛋白","素食"]',

    -- 烹饪信息
    cook_time VARCHAR(30) COMMENT '烹饪时间，如"30分钟"',
    prep_time VARCHAR(30) COMMENT '准备时间，如"10分钟"',
    servings INT DEFAULT 2 COMMENT '份量（几人份）',
    difficulty VARCHAR(20) DEFAULT '简单' COMMENT '难度：简单/中等/困难',

    -- 营养信息（每份）
    calories INT COMMENT '热量 kcal/份',
    protein FLOAT COMMENT '蛋白质 g/份',
    fat FLOAT COMMENT '脂肪 g/份',
    carbs FLOAT COMMENT '碳水化合物 g/份',
    fiber FLOAT COMMENT '膳食纤维 g/份',
    sodium FLOAT COMMENT '钠 mg/份',

    -- 食材与步骤（JSON格式）
    ingredients TEXT COMMENT '食材JSON数组',
    steps TEXT COMMENT '步骤JSON数组',

    -- 额外信息
    tips TEXT COMMENT '烹饪小贴士',
    suitable_for TEXT COMMENT '适合人群描述',
    not_suitable_for TEXT COMMENT '不适合人群描述',

    -- 统计与状态
    favorite_count INT DEFAULT 0 COMMENT '收藏数',
    view_count INT DEFAULT 0 COMMENT '浏览数',
    is_featured TINYINT(1) DEFAULT 0 COMMENT '是否为推荐/精选',
    is_active TINYINT(1) DEFAULT 1 COMMENT '是否上架',
    sort_order INT DEFAULT 0 COMMENT '排序权重',

    -- 元数据
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',

    INDEX idx_recipe_category (category),
    INDEX idx_recipe_featured (is_featured, is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='精品食谱表';


-- =====================================================
-- 14. 用户收藏表
-- =====================================================
CREATE TABLE IF NOT EXISTS `user_favorite` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    recipe_id INT NOT NULL COMMENT '食谱ID',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',

    UNIQUE KEY uq_user_recipe (user_id, recipe_id),
    FOREIGN KEY (user_id) REFERENCES `user`(id) ON DELETE CASCADE,
    FOREIGN KEY (recipe_id) REFERENCES premium_recipes(id) ON DELETE CASCADE,
    INDEX idx_favorite_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏关系表';


-- =====================================================
-- 插入初始数据
-- =====================================================

-- 烹饪方式
INSERT IGNORE INTO cooking_method (name, calorie_adjust, calorie_percent, description, icon, sort_order) VALUES
('清蒸', -20, -10, '保留原味，几乎不加油', '🫕', 1),
('水煮', -10, -5, '少油少盐，相对健康', '♨️', 2),
('少油炒', 0, 0, '正常烹饪，作为基准', '🍳', 3),
('红烧', 50, 20, '加糖加油，热量增加', '🥘', 4),
('油炸', 150, 50, '大量用油，热量大增', '🍟', 5);

-- 通用份量
INSERT IGNORE INTO food_portion (category, portion_name, calorie_factor, is_default, sort_order) VALUES
(NULL, '小份', 0.6, 0, 1),
(NULL, '中份', 1.0, 1, 2),
(NULL, '大份', 1.5, 0, 3);


-- =====================================================
-- 完成！共 14 张表
-- =====================================================
-- 表清单:
--   1.  user               - 用户表
--   2.  food               - 食物主表
--   3.  food_temp          - 临时食物表
--   4.  food_contraindication - 食物禁忌表
--   5.  food_portion       - 食物份量选项表
--   6.  cooking_method     - 烹饪方式表
--   7.  recognition_history - 识别历史表
--   8.  meal_record        - 饮食记录表
--   9.  weight_record      - 体重记录表
--  10.  diet_plan          - 食谱计划表
--  11.  diet_plan_day      - 食谱每日安排表
--  12.  diet_plan_meal     - 食谱具体餐单表
--  13.  premium_recipes    - 精品食谱表
--  14.  user_favorite      - 用户收藏关系表
-- =====================================================
