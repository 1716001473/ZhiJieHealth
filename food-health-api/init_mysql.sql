-- =====================================================
-- 智能食物识别健康助手 - MySQL 数据库初始化脚本
-- =====================================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS food_health DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE food_health;

-- =====================================================
-- 1. 用户表
-- =====================================================
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(200) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),

    -- 健康档案
    health_conditions TEXT COMMENT '健康状况',
    allergies TEXT COMMENT '过敏原',

    -- 个性化目标与偏好
    health_goal VARCHAR(50) DEFAULT 'maintain' COMMENT '健康目标：lose_weight/gain_muscle/maintain',
    dietary_preferences TEXT COMMENT '饮食偏好',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 2. 食物表
-- =====================================================
CREATE TABLE IF NOT EXISTS food (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    alias VARCHAR(200),
    category VARCHAR(50),

    -- 营养数据（每100g）
    calories DECIMAL(10,2),
    protein DECIMAL(10,2),
    fat DECIMAL(10,2),
    carbohydrate DECIMAL(10,2),
    fiber DECIMAL(10,2),
    sodium DECIMAL(10,2),
    sugar DECIMAL(10,2),

    -- 份量参考
    serving_desc VARCHAR(100),
    serving_weight INT DEFAULT 100,

    -- 健康评级
    health_rating VARCHAR(20) DEFAULT '适量',
    health_tips TEXT,

    -- 元数据
    image_url VARCHAR(500),
    source VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_name (name),
    INDEX idx_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 3. 食物禁忌表
-- =====================================================
CREATE TABLE IF NOT EXISTS food_contraindication (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT,
    food_keyword VARCHAR(100),

    condition_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT '慎食',
    reason TEXT,
    suggestion TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (food_id) REFERENCES food(id) ON DELETE CASCADE,
    INDEX idx_condition (condition_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 4. 食物份量表
-- =====================================================
CREATE TABLE IF NOT EXISTS food_portion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    food_id INT,
    category VARCHAR(50),

    portion_name VARCHAR(50) NOT NULL,
    weight_grams INT,
    calorie_factor DECIMAL(3,2) DEFAULT 1.0,

    is_default BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,

    FOREIGN KEY (food_id) REFERENCES food(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 5. 烹饪方式表
-- =====================================================
CREATE TABLE IF NOT EXISTS cooking_method (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    calorie_adjust INT DEFAULT 0,
    calorie_percent DECIMAL(5,2) DEFAULT 0,
    description VARCHAR(200),
    sort_order INT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 6. 识别历史表
-- =====================================================
CREATE TABLE IF NOT EXISTS recognition_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    image_url VARCHAR(500),
    recognized_food VARCHAR(100) NOT NULL,
    confidence DECIMAL(5,4),
    alternatives TEXT,

    -- 用户确认的参数
    selected_portion VARCHAR(50),
    selected_cooking VARCHAR(50),

    -- 计算结果
    final_calories_min INT,
    final_calories_max INT,

    -- 元数据
    meal_type VARCHAR(20),
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 7. 饮食记录表
-- =====================================================
CREATE TABLE IF NOT EXISTS meal_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    record_date DATE NOT NULL,
    meal_type VARCHAR(20) NOT NULL,

    food_id INT,
    food_name VARCHAR(100),
    amount_desc VARCHAR(50),
    cooking_method VARCHAR(50),
    calories_min INT,
    calories_max INT,

    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_date (user_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 8. 体重记录表
-- =====================================================
CREATE TABLE IF NOT EXISTS weight_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    weight DECIMAL(5,2) NOT NULL,
    record_date DATE NOT NULL,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_user_date (user_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 9. 食谱计划表
-- =====================================================
CREATE TABLE IF NOT EXISTS diet_plan (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    cover_image VARCHAR(500),

    -- 基本属性
    duration_days INT DEFAULT 7,
    target_user VARCHAR(200),
    difficulty VARCHAR(20) DEFAULT 'medium',

    -- 增强属性
    tags VARCHAR(500),
    source VARCHAR(20) DEFAULT 'preset',
    author_id INT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 10. 食谱计划日表
-- =====================================================
CREATE TABLE IF NOT EXISTS diet_plan_day (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plan_id INT NOT NULL,
    day_index INT NOT NULL,
    title VARCHAR(200),
    total_calories INT DEFAULT 0,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (plan_id) REFERENCES diet_plan(id) ON DELETE CASCADE,
    INDEX idx_plan (plan_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 11. 食谱计划餐次表
-- =====================================================
CREATE TABLE IF NOT EXISTS diet_plan_meal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day_id INT NOT NULL,
    meal_type VARCHAR(20) NOT NULL,
    sort_order INT,
    food_name VARCHAR(100),
    amount_desc VARCHAR(50),
    calories INT DEFAULT 0,
    alternatives VARCHAR(500),

    FOREIGN KEY (day_id) REFERENCES diet_plan_day(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- 插入初始数据
-- =====================================================

-- 烹饪方式
INSERT IGNORE INTO cooking_method (name, calorie_adjust, calorie_percent, description, sort_order) VALUES
('清蒸', -20, -10, '保留原味，几乎不加油', 1),
('水煮', -10, -5, '少油少盐，相对健康', 2),
('少油炒', 0, 0, '正常烹饪，作为基准', 3),
('红烧', 50, 20, '加糖加油，热量增加', 4),
('油炸', 150, 50, '大量用油，热量大增', 5);

-- 通用份量
INSERT IGNORE INTO food_portion (category, portion_name, calorie_factor, is_default, sort_order) VALUES
(NULL, '小份', 0.6, FALSE, 1),
(NULL, '中份', 1.0, TRUE, 2),
(NULL, '大份', 1.5, FALSE, 3);

-- =====================================================
-- 完成！
-- =====================================================
