# 🍎 智能食物识别健康助手 - 项目计划书

> **版本**: v0.1.0 (初稿)  
> **创建时间**: 2026-01-23  
> **最后更新**: 2026-01-23  
> **状态**: 规划阶段

---

## 📋 目录

- [项目概述](#项目概述)
- [核心功能](#核心功能)
- [技术栈选型](#技术栈选型)
- [系统架构](#系统架构)
- [数据库设计](#数据库设计)
- [项目目录结构](#项目目录结构)
- [开发阶段规划](#开发阶段规划)
- [API接口设计](#api接口设计)
- [卡路里估算方案](#卡路里估算方案)
- [第三方服务](#第三方服务)
- [待确认事项](#待确认事项)
- [更新日志](#更新日志)

---

## 📖 项目概述

### 项目愿景

打造一款**简单实用**的健康饮食助手，用户通过拍照即可识别食物，获取营养信息和健康建议，帮助用户更好地管理饮食健康。

### 项目定位

| 维度 | 决策 |
|------|------|
| **产品形态** | 微信小程序（首发）→ 后期过渡到 App |
| **目标用户** | 关注饮食健康的普通用户、减肥人群、特定疾病患者 |
| **开发目标** | 本地开发验证 → 上线运营 |
| **商业模式** | 暂定免费，后期可考虑会员增值服务 |

### 竞品参考

- **薄荷健康**：功能全面，数据库庞大，但操作复杂
- **本项目差异化**：
  - 更简单：拍照即出结果，无需手动搜索
  - 更聚焦：专注食物识别 + 健康建议，不做社区/电商
  - 更诚实：卡路里给范围值，不给虚假精确值

---

## 🎯 核心功能

### 功能优先级矩阵

| 优先级 | 功能 | 说明 | 状态 |
|--------|------|------|------|
| **P0** | 拍照识别食物 | 调用AI识别，返回菜品名称 | ⏳ 待开发 |
| **P0** | 营养数据展示 | 热量、蛋白质、脂肪、碳水等 | ⏳ 待开发 |
| **P0** | 健康食用建议 | 基于食物特性给出建议 | ⏳ 待开发 |
| **P0** | 不适宜人群警告 | 糖尿病、高血压、痛风等禁忌提醒 | ⏳ 待开发 |
| **P1** | 卡路里估算 | 交互确认份量 + 模糊范围值 | ⏳ 待开发 |
| **P1** | 识别历史记录 | 记录用户的识别历史 | ⏳ 待开发 |
| **P2** | 用户系统 | 微信登录、个人设置 | ⏳ 待开发 |
| **P2** | 个人健康档案 | 记录用户疾病/过敏信息，个性化提醒 | ⏳ 待开发 |
| **P3** | 每日饮食打卡 | 记录每日摄入，统计分析 | ⏳ 待开发 |

### 核心用户流程

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  首页   │ → │ 拍照/   │ → │  AI     │ → │ 份量    │ → │ 结果    │
│         │    │ 选择图片 │    │  识别   │    │ 确认    │    │ 展示    │
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
                                                               │
                                              ┌────────────────┘
                                              ▼
                                        ┌─────────┐
                                        │ 保存到  │
                                        │ 历史记录│
                                        └─────────┘
```

---

## 🛠️ 技术栈选型

### 整体技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户端                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              UniApp + Vue 3 + TypeScript                │   │
│  │    ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │    │ 拍照/相册 │  │ 结果展示  │  │ 历史记录 │            │   │
│  │    └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────┘   │
│              编译输出：微信小程序 / App / H5                     │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTPS
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         后端服务                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Python FastAPI + SQLAlchemy                │   │
│  │    ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │    │ 图像识别  │  │ 营养查询  │  │ 用户管理 │            │   │
│  │    │  代理层   │  │   服务   │  │   服务   │            │   │
│  │    └──────────┘  └──────────┘  └──────────┘            │   │
│  └─────────────────────────────────────────────────────────┘   │
│              部署：本地开发 → 云服务器（阿里云/腾讯云）           │
└─────────────────────────────────────────────────────────────────┘
           │                    │                    │
           ▼                    ▼                    ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   百度AI       │    │   MySQL       │    │   Redis       │
│   菜品识别     │    │   数据库      │    │   缓存(可选)   │
└───────────────┘    └───────────────┘    └───────────────┘
```

### 前端技术栈

| 技术 | 版本 | 选择理由 |
|------|------|----------|
| **UniApp** | 3.x | 一套代码编译到小程序/App/H5，后期过渡成本为零 |
| **Vue 3** | 3.4+ | Composition API更灵活，生态成熟 |
| **TypeScript** | 5.x | 类型安全，减少Bug |
| **Pinia** | 2.x | 状态管理（替代Vuex），更简洁 |
| **uView UI** | 2.x | UniApp专用UI组件库，美观且兼容性好 |

**选择 UniApp 的理由：**
- ✅ 后期一键编译成 Android/iOS App，无需重写
- ✅ Vue语法，无需学习新框架
- ✅ 生态成熟，组件库丰富
- ✅ HBuilderX IDE支持，开发体验好

### 后端技术栈

| 技术 | 版本 | 选择理由 |
|------|------|----------|
| **Python** | 3.11+ | AI生态最好，后期训练模型无缝衔接 |
| **FastAPI** | 0.110+ | 性能媲美Go，自动生成API文档，异步支持 |
| **SQLAlchemy** | 2.x | ORM框架，切换数据库无成本 |
| **Pydantic** | 2.x | 数据验证，类型安全 |
| **Uvicorn** | 0.27+ | ASGI服务器，生产级性能 |
| **httpx** | 0.27+ | 异步HTTP客户端，调用百度AI |

**选择 Python FastAPI 的理由：**

| 对比项 | Python FastAPI | Java Spring Boot |
|--------|---------------|------------------|
| AI API调用 | 3行代码搞定 | 需要大量样板代码 |
| 开发速度 | 快 | 较慢 |
| 后期训练模型 | 无缝使用 PyTorch/TensorFlow | 需要单独搭建Python服务 |
| 部署成本 | 内存占用小 | JVM启动慢、占内存 |

### 数据库

| 阶段 | 数据库 | 说明 |
|------|--------|------|
| **开发阶段** | SQLite | 零配置，文件存储，方便本地开发 |
| **上线阶段** | MySQL 8.0 | 稳定可靠，性能好 |
| **缓存(可选)** | Redis | 热门食物数据缓存，提升性能 |

---

## 🗄️ 数据库设计

### ER图

```
┌─────────────────┐       ┌─────────────────────┐
│      food       │       │ food_contraindication│
├─────────────────┤       ├─────────────────────┤
│ id (PK)         │──────<│ food_id (FK)        │
│ name            │       │ condition_type      │
│ category        │       │ severity            │
│ calories        │       │ reason              │
│ protein         │       │ suggestion          │
│ fat             │       └─────────────────────┘
│ carbohydrate    │
│ health_rating   │       ┌─────────────────────┐
│ health_tips     │       │    food_portion     │
└─────────────────┘       ├─────────────────────┤
         │                │ food_id (FK)        │
         └───────────────<│ portion_name        │
                          │ weight_grams        │
                          │ calorie_factor      │
                          └─────────────────────┘

┌─────────────────┐       ┌─────────────────────┐
│  cooking_method │       │ recognition_history │
├─────────────────┤       ├─────────────────────┤
│ id (PK)         │       │ id (PK)             │
│ name            │       │ user_id             │
│ calorie_adjust  │       │ image_url           │
│ description     │       │ recognized_food     │
└─────────────────┘       │ final_calories      │
                          │ created_at          │
                          └─────────────────────┘
```

### 表结构详细设计

```sql
-- =====================================================
-- 1. 食物/菜品表
-- =====================================================
CREATE TABLE food (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(100) NOT NULL UNIQUE,   -- 菜品名称
    alias           VARCHAR(200),                   -- 别名（逗号分隔）
    category        VARCHAR(50),                    -- 分类：主食/荤菜/素菜/汤类/饮品/水果/零食
    
    -- 营养数据（每100g）
    calories        DECIMAL(10,2),                  -- 热量 kcal
    protein         DECIMAL(10,2),                  -- 蛋白质 g
    fat             DECIMAL(10,2),                  -- 脂肪 g
    carbohydrate    DECIMAL(10,2),                  -- 碳水化合物 g
    fiber           DECIMAL(10,2),                  -- 膳食纤维 g
    sodium          DECIMAL(10,2),                  -- 钠 mg
    sugar           DECIMAL(10,2),                  -- 糖 g
    
    -- 份量参考
    serving_desc    VARCHAR(100),                   -- 常规份量描述：如"一盘约200g"
    serving_weight  INTEGER DEFAULT 100,            -- 常规份量重量 g
    
    -- 健康评级
    health_rating   VARCHAR(20) DEFAULT '适量',     -- 健康评级：推荐/适量/少食
    health_tips     TEXT,                           -- 健康提示/食用建议
    
    -- 元数据
    image_url       VARCHAR(500),                   -- 示例图片
    source          VARCHAR(100),                   -- 数据来源
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. 禁忌规则表（不适宜人群）
-- =====================================================
CREATE TABLE food_contraindication (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id         INTEGER,                        -- 关联食物（可为空，表示通用规则）
    food_keyword    VARCHAR(100),                   -- 食物关键词（模糊匹配用）
    
    condition_type  VARCHAR(50) NOT NULL,           -- 疾病/人群类型
    -- 可选值：糖尿病/高血压/痛风/高血脂/肾病/孕妇/哺乳期/婴幼儿/过敏体质/胃病
    
    severity        VARCHAR(20) NOT NULL DEFAULT '慎食',  -- 严重程度：禁食/慎食/少食
    reason          TEXT,                           -- 原因说明
    suggestion      TEXT,                           -- 替代建议
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (food_id) REFERENCES food(id) ON DELETE CASCADE
);

-- =====================================================
-- 3. 食物份量选项表（用于卡路里交互确认）
-- =====================================================
CREATE TABLE food_portion (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    food_id         INTEGER,                        -- 关联特定食物（可为空表示通用）
    category        VARCHAR(50),                    -- 或关联分类
    
    portion_name    VARCHAR(50) NOT NULL,           -- 份量名称：小份/中份/大份/一碗/一盘
    weight_grams    INTEGER,                        -- 对应重量 g
    calorie_factor  DECIMAL(3,2) DEFAULT 1.0,       -- 热量系数：0.6/1.0/1.5
    
    is_default      BOOLEAN DEFAULT FALSE,          -- 是否默认选项
    sort_order      INTEGER DEFAULT 0,              -- 排序顺序
    
    FOREIGN KEY (food_id) REFERENCES food(id) ON DELETE CASCADE
);

-- =====================================================
-- 4. 烹饪方式修正表（用于卡路里调整）
-- =====================================================
CREATE TABLE cooking_method (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(50) NOT NULL UNIQUE,    -- 烹饪方式：清蒸/水煮/少油炒/红烧/油炸
    calorie_adjust  INTEGER DEFAULT 0,              -- 热量调整值 kcal（正数增加，负数减少）
    calorie_percent DECIMAL(5,2) DEFAULT 0,         -- 热量调整百分比
    description     VARCHAR(200),                   -- 说明
    icon            VARCHAR(50),                    -- 图标名称
    sort_order      INTEGER DEFAULT 0
);

-- =====================================================
-- 5. 用户识别历史表
-- =====================================================
CREATE TABLE recognition_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         VARCHAR(100),                   -- 用户标识（微信openid或设备ID）
    
    -- 识别信息
    image_url       VARCHAR(500),                   -- 原始图片地址
    recognized_food VARCHAR(100),                   -- 识别结果（菜品名称）
    confidence      DECIMAL(5,4),                   -- 置信度 0-1
    alternatives    TEXT,                           -- 其他候选结果 JSON
    
    -- 用户确认的参数
    selected_portion VARCHAR(50),                   -- 用户选择的份量
    selected_cooking VARCHAR(50),                   -- 用户选择的烹饪方式
    
    -- 计算结果
    final_calories_min INTEGER,                     -- 估算热量下限
    final_calories_max INTEGER,                     -- 估算热量上限
    
    -- 元数据
    meal_type       VARCHAR(20),                    -- 餐次：早餐/午餐/晚餐/加餐
    note            TEXT,                           -- 用户备注
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 6. 用户表（后期扩展）
-- =====================================================
CREATE TABLE user (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    openid          VARCHAR(100) UNIQUE,            -- 微信openid
    nickname        VARCHAR(100),                   -- 昵称
    avatar_url      VARCHAR(500),                   -- 头像
    
    -- 健康档案（用于个性化提醒）
    health_conditions TEXT,                         -- 健康状况 JSON数组
    -- 如：["糖尿病", "高血压"]
    
    allergies       TEXT,                           -- 过敏原 JSON数组
    -- 如：["花生", "海鲜"]
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 索引
-- =====================================================
CREATE INDEX idx_food_name ON food(name);
CREATE INDEX idx_food_category ON food(category);
CREATE INDEX idx_contraindication_condition ON food_contraindication(condition_type);
CREATE INDEX idx_history_user ON recognition_history(user_id);
CREATE INDEX idx_history_created ON recognition_history(created_at);
```

### 初始数据示例

```sql
-- 烹饪方式
INSERT INTO cooking_method (name, calorie_adjust, calorie_percent, description, sort_order) VALUES
('清蒸', -20, -10, '保留原味，几乎不加油', 1),
('水煮', -10, -5, '少油少盐，相对健康', 2),
('少油炒', 0, 0, '正常烹饪，作为基准', 3),
('红烧', 50, 20, '加糖加油，热量增加', 4),
('油炸', 150, 50, '大量用油，热量大增', 5);

-- 通用份量
INSERT INTO food_portion (category, portion_name, calorie_factor, is_default, sort_order) VALUES
(NULL, '小份', 0.6, FALSE, 1),
(NULL, '中份', 1.0, TRUE, 2),
(NULL, '大份', 1.5, FALSE, 3);

-- 通用禁忌规则
INSERT INTO food_contraindication (food_keyword, condition_type, severity, reason, suggestion) VALUES
('糖', '糖尿病', '慎食', '含糖量高，可能导致血糖快速升高', '建议选择低GI食物'),
('油炸', '高血脂', '少食', '油炸食品脂肪含量高', '建议清蒸或水煮'),
('海鲜', '痛风', '慎食', '海鲜嘌呤含量较高', '急性发作期应禁食'),
('海鲜', '过敏体质', '慎食', '常见过敏原', '首次食用请少量尝试'),
('腌制', '高血压', '少食', '钠含量高', '建议选择新鲜食材'),
('生冷', '孕妇', '慎食', '可能存在细菌污染风险', '建议食用熟食'),
('辛辣', '胃病', '少食', '刺激胃黏膜', '建议清淡饮食');
```

---

## 📁 项目目录结构

### 后端 (Python FastAPI)

```
food-health-api/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI 应用入口
│   ├── config.py                   # 配置管理（环境变量、API密钥）
│   │
│   ├── api/                        # API路由层
│   │   ├── __init__.py
│   │   ├── v1/                     # API版本控制
│   │   │   ├── __init__.py
│   │   │   ├── recognition.py      # 食物识别接口
│   │   │   ├── nutrition.py        # 营养信息接口
│   │   │   ├── history.py          # 历史记录接口
│   │   │   └── user.py             # 用户接口
│   │   └── deps.py                 # 依赖注入
│   │
│   ├── services/                   # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── baidu_ai.py             # 百度AI菜品识别封装
│   │   ├── food_service.py         # 食物数据服务
│   │   ├── nutrition_service.py    # 营养计算服务
│   │   ├── contraindication_service.py  # 禁忌规则服务
│   │   └── calorie_calculator.py   # 卡路里估算器
│   │
│   ├── models/                     # SQLAlchemy 数据库模型
│   │   ├── __init__.py
│   │   ├── food.py                 # 食物模型
│   │   ├── contraindication.py     # 禁忌规则模型
│   │   ├── history.py              # 历史记录模型
│   │   └── user.py                 # 用户模型
│   │
│   ├── schemas/                    # Pydantic 数据结构
│   │   ├── __init__.py
│   │   ├── food.py                 # 食物相关Schema
│   │   ├── recognition.py          # 识别相关Schema
│   │   └── response.py             # 通用响应Schema
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py           # 数据库连接配置
│   │   ├── session.py              # Session管理
│   │   └── init_data.py            # 初始化数据脚本
│   │
│   └── utils/
│       ├── __init__.py
│       └── helpers.py              # 工具函数
│
├── data/
│   ├── foods.json                  # 食物营养数据（初始数据）
│   ├── contraindications.json      # 禁忌规则数据
│   └── cooking_methods.json        # 烹饪方式数据
│
├── tests/                          # 单元测试
│   ├── __init__.py
│   ├── test_recognition.py
│   └── test_nutrition.py
│
├── alembic/                        # 数据库迁移（可选）
│   └── versions/
│
├── .env.example                    # 环境变量模板
├── .env                            # 环境变量（不提交git）
├── .gitignore
├── requirements.txt                # Python依赖
├── Dockerfile                      # Docker部署（可选）
└── README.md
```

### 前端 (UniApp + Vue 3)

```
food-health-app/
├── src/
│   ├── pages/                      # 页面
│   │   ├── index/                  # 首页
│   │   │   └── index.vue
│   │   ├── camera/                 # 拍照页面
│   │   │   └── index.vue
│   │   ├── result/                 # 识别结果页
│   │   │   └── index.vue
│   │   ├── confirm/                # 份量确认页
│   │   │   └── index.vue
│   │   ├── detail/                 # 食物详情页
│   │   │   └── index.vue
│   │   ├── history/                # 历史记录页
│   │   │   └── index.vue
│   │   └── profile/                # 个人中心
│   │       └── index.vue
│   │
│   ├── components/                 # 公共组件
│   │   ├── FoodCard.vue            # 食物卡片
│   │   ├── NutritionChart.vue      # 营养环形图
│   │   ├── CalorieRange.vue        # 卡路里范围显示
│   │   ├── PortionSelector.vue     # 份量选择器
│   │   ├── CookingSelector.vue     # 烹饪方式选择器
│   │   ├── WarningBadge.vue        # 禁忌警告徽章
│   │   ├── HealthTips.vue          # 健康建议卡片
│   │   └── LoadingOverlay.vue      # 加载遮罩
│   │
│   ├── api/                        # API请求
│   │   ├── index.ts                # API统一出口
│   │   ├── recognition.ts          # 识别相关API
│   │   ├── food.ts                 # 食物相关API
│   │   └── user.ts                 # 用户相关API
│   │
│   ├── stores/                     # Pinia状态管理
│   │   ├── index.ts
│   │   ├── user.ts                 # 用户状态
│   │   └── recognition.ts          # 识别状态
│   │
│   ├── utils/
│   │   ├── request.ts              # 请求封装
│   │   ├── storage.ts              # 本地存储
│   │   └── helpers.ts              # 工具函数
│   │
│   ├── types/                      # TypeScript类型定义
│   │   ├── food.d.ts
│   │   └── api.d.ts
│   │
│   ├── static/                     # 静态资源
│   │   ├── images/
│   │   └── icons/
│   │
│   ├── styles/                     # 全局样式
│   │   ├── variables.scss          # SCSS变量
│   │   └── common.scss             # 公共样式
│   │
│   ├── App.vue                     # 根组件
│   ├── main.ts                     # 入口文件
│   ├── manifest.json               # 应用配置
│   ├── pages.json                  # 页面配置
│   └── uni.scss                    # UniApp全局样式变量
│
├── .gitignore
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

---

## 📅 开发阶段规划

### Phase 1: 基础框架搭建（Week 1-2）

**目标**: 跑通完整流程，实现最小可用版本

| 任务 | 优先级 | 状态 |
|------|--------|------|
| 后端项目初始化（FastAPI + SQLAlchemy） | P0 | ⏳ |
| 数据库表创建 | P0 | ⏳ |
| 百度AI账号申请 + API对接 | P0 | ⏳ |
| 前端项目初始化（UniApp + Vue3） | P0 | ⏳ |
| 拍照/选图功能 | P0 | ⏳ |
| 调用后端识别接口 | P0 | ⏳ |
| 基础结果展示页面 | P0 | ⏳ |

**交付物**: 能拍照 → 识别出菜品名称 → 显示基本信息

### Phase 2: 核心功能完善（Week 3-4）

**目标**: 完成所有P0/P1功能

| 任务 | 优先级 | 状态 |
|------|--------|------|
| 食物营养数据库（录入100+常见菜品） | P0 | ⏳ |
| 营养数据展示（热量、三大营养素） | P0 | ⏳ |
| 健康食用建议 | P0 | ⏳ |
| 禁忌人群警告 | P0 | ⏳ |
| 份量选择交互 | P1 | ⏳ |
| 烹饪方式选择 | P1 | ⏳ |
| 卡路里范围估算 | P1 | ⏳ |
| 识别历史记录 | P1 | ⏳ |

**交付物**: 功能完整的识别 + 建议系统

### Phase 3: 体验优化（Week 5-6）

**目标**: 打磨UI/UX，准备上线

| 任务 | 优先级 | 状态 |
|------|--------|------|
| UI视觉设计优化 | P1 | ⏳ |
| 加载动画、过渡效果 | P2 | ⏳ |
| 错误处理优化 | P1 | ⏳ |
| 数据扩充（500+菜品） | P2 | ⏳ |
| 微信登录集成 | P2 | ⏳ |
| 个人健康档案 | P2 | ⏳ |

**交付物**: 可上线的完整产品

### Phase 4: 上线运营（Week 7+）

| 任务 | 说明 |
|------|------|
| 服务器部署 | 阿里云/腾讯云 |
| 域名备案 | 小程序必须 |
| 小程序审核提交 | 微信平台 |
| 监控告警配置 | 日志、性能监控 |
| 用户反馈收集 | 迭代优化 |

---

## 🔌 API接口设计

### 接口总览

| 模块 | 接口 | 方法 | 说明 |
|------|------|------|------|
| 识别 | `/api/v1/recognize` | POST | 上传图片识别食物 |
| 食物 | `/api/v1/food/{name}` | GET | 获取食物详情 |
| 食物 | `/api/v1/food/{name}/nutrition` | GET | 获取营养数据 |
| 食物 | `/api/v1/food/{name}/contraindications` | GET | 获取禁忌信息 |
| 计算 | `/api/v1/calculate/calories` | POST | 计算卡路里 |
| 历史 | `/api/v1/history` | GET | 获取识别历史 |
| 历史 | `/api/v1/history` | POST | 保存识别记录 |

### 核心接口详细设计

#### 1. 食物识别接口

```
POST /api/v1/recognize
Content-Type: multipart/form-data

Request:
  - image: File (图片文件)
  
Response:
{
  "code": 0,
  "message": "success",
  "data": {
    "results": [
      {
        "name": "宫保鸡丁",
        "confidence": 0.92,
        "category": "荤菜"
      },
      {
        "name": "辣子鸡",
        "confidence": 0.05,
        "category": "荤菜"
      }
    ],
    "top_result": {
      "name": "宫保鸡丁",
      "confidence": 0.92,
      "nutrition": {
        "calories": 180,
        "protein": 15.2,
        "fat": 10.5,
        "carbohydrate": 8.3
      },
      "health_rating": "适量",
      "health_tips": "蛋白质丰富，但油脂较多，建议适量食用",
      "contraindications": [
        {
          "condition": "高血脂",
          "severity": "少食",
          "reason": "油炸花生脂肪含量高"
        }
      ]
    }
  }
}
```

#### 2. 卡路里计算接口

```
POST /api/v1/calculate/calories
Content-Type: application/json

Request:
{
  "food_name": "宫保鸡丁",
  "portion": "中份",          // 小份/中份/大份
  "cooking_method": "少油炒"   // 清蒸/水煮/少油炒/红烧/油炸
}

Response:
{
  "code": 0,
  "data": {
    "food_name": "宫保鸡丁",
    "base_calories": 180,       // 每100g基础热量
    "portion_weight": 200,      // 估算重量
    "portion_factor": 1.0,      // 份量系数
    "cooking_adjust": 0,        // 烹饪方式调整
    
    "calories_min": 320,        // 热量下限
    "calories_max": 400,        // 热量上限
    "calories_display": "320~400 kcal",
    
    "breakdown": {
      "base": "180 kcal/100g × 200g = 360 kcal",
      "cooking_adjust": "+0 kcal (少油炒)",
      "range_reason": "根据实际用油量，热量可能在 ±40kcal 范围内浮动"
    }
  }
}
```

---

## 🧮 卡路里估算方案

### 设计理念

**不追求虚假的精确，追求有价值的模糊**

用户拍照后，系统给出的不是一个精确数字（这本身就是不可能的），而是：
1. 一个**合理的范围值** + 
2. 用户可以**交互调整**的参数 +
3. **透明的计算逻辑**

### 计算公式

```
最终热量范围 = 基础热量 × 份量系数 × 烹饪系数 ± 浮动范围

其中：
- 基础热量：每100g的热量（来自数据库）
- 份量系数：小份(0.6) / 中份(1.0) / 大份(1.5)
- 烹饪系数：清蒸(0.9) / 水煮(0.95) / 少油炒(1.0) / 红烧(1.2) / 油炸(1.5)
- 浮动范围：±15%（考虑实际差异）
```

### 交互流程

```
┌─────────────────────────────────────────────────────────────────┐
│                        识别结果页                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   🍗 宫保鸡丁                              置信度: 92%           │
│                                                                  │
│   ────────────────────────────────────────────────────────────  │
│                                                                  │
│   📊 基础营养（每100g）                                          │
│   热量: 180 kcal | 蛋白质: 15.2g | 脂肪: 10.5g | 碳水: 8.3g     │
│                                                                  │
│   ────────────────────────────────────────────────────────────  │
│                                                                  │
│   🍽️ 估算你这份的热量                                           │
│                                                                  │
│   份量选择:  [ 小份 ]  [●中份●]  [ 大份 ]                        │
│                                                                  │
│   烹饪方式:  清蒸  水煮  [●少油炒●]  红烧  油炸                  │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │              🔥 预估热量: 320 ~ 400 kcal                 │  │
│   │                                                          │  │
│   │         （基于中份约200g，少油炒方式计算）                 │  │
│   │                                                          │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
│   ⚠️ 提示：实际热量受具体用油量、配料比例影响，仅供参考          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔗 第三方服务

### 百度AI 菜品识别

- **接口文档**: https://ai.baidu.com/ai-doc/IMAGERECOGNITION/Kk3bcxg1t
- **价格**: 500次/天免费，超出约 0.003元/次
- **申请步骤**:
  1. 注册百度AI开放平台账号
  2. 创建应用，选择"图像识别 - 菜品识别"
  3. 获取 `API_KEY` 和 `SECRET_KEY`

### 调用示例 (Python)

```python
import httpx

class BaiduAIService:
    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None
    
    async def get_access_token(self):
        """获取百度AI访问令牌"""
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params)
            self.access_token = response.json()["access_token"]
        return self.access_token
    
    async def recognize_dish(self, image_base64: str):
        """识别菜品"""
        if not self.access_token:
            await self.get_access_token()
        
        url = f"https://aip.baidubce.com/rest/2.0/image-classify/v2/dish"
        params = {"access_token": self.access_token}
        data = {"image": image_base64, "top_num": 5}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params, data=data)
            return response.json()
```

---

## ❓ 待确认事项

### 技术决策

- [ ] **后端语言确认**: Python FastAPI（推荐）还是 Java Spring Boot？
- [ ] **是否需要Docker部署**: 本地开发可以不用，上线建议用
- [ ] **图片存储方案**: 本地存储 / 阿里云OSS / 腾讯云COS

### 产品决策

- [ ] **项目名称**: 需要起一个正式的产品名称
- [ ] **UI设计风格**: 清新健康风 / 专业医疗风 / 年轻活力风
- [ ] **是否需要离线功能**: 无网络时是否需要基础功能

### 数据决策

- [ ] **初始数据量**: 先录入多少菜品？（建议100-200条起步）
- [ ] **数据来源**: 手动收集 / 爬取 / 购买？
- [ ] **禁忌规则覆盖范围**: 覆盖哪些疾病人群？

---

## 📝 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-01-23 | v0.1.0 | 初始版本，完成技术方案设计 |

---

> 📌 **下一步**: 确认上述待确认事项后，开始 Phase 1 开发
