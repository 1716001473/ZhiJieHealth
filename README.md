# 🍎 智能食物识别健康助手 - 后端 API

基于 FastAPI 构建的智能食物识别与营养健康管理后端服务，集成百度 AI 图像识别和 DeepSeek AI 智能分析能力。

## ✨ 核心功能

### 🔍 食物识别与营养分析
- **AI 图像识别**：基于百度 AI 的菜品识别（支持模拟数据模式）
- **营养数据库**：内置 30+ 常见中餐菜品的详细营养信息
- **智能计算**：根据烹饪方式和份量精确计算卡路里

### 📊 饮食记录与分析
- **每日记录**：记录早中晚餐及加餐的详细饮食数据
- **营养统计**：自动汇总每日热量、蛋白质、脂肪、碳水化合物摄入
- **趋势分析**：查看近 7/30 天的营养摄入趋势图表
- **批量操作**：支持批量添加、编辑、删除饮食记录

### 🎯 AI 智能食谱生成
- **个性化推荐**：基于用户健康档案（身高、体重、年龄、性别、活动量）生成定制食谱
- **目标导向**：支持减重、增肌、保持健康等不同健康目标
- **偏好适配**：根据饮食偏好（素食、低碳水等）和不喜欢的食材标签智能筛选
- **食谱管理**：查看、应用、重新生成 AI 食谱计划
- **一键应用**：将食谱中的某一天直接应用到每日饮食记录

### 💪 健康建议与体重管理
- **BMI 计算**：自动计算并评估身体质量指数
- **智能建议**：基于 DeepSeek AI 生成个性化饮食与运动建议
- **体重追踪**：记录每日体重，查看历史趋势
- **健康档案**：维护用户完整的健康信息

### 👤 用户系统
- **用户注册/登录**：支持手机号注册和登录
- **健康档案管理**：维护身高、体重、年龄、性别等基础信息
- **偏好设置**：保存饮食偏好和健康目标

## 🛠 技术栈

- **Python** 3.11+
- **FastAPI** 0.115.0 - 高性能异步 Web 框架
- **SQLAlchemy** 2.0.35 - ORM 数据库操作
- **SQLite** - 轻量级开发数据库
- **Pydantic** 2.9.2 - 数据验证与序列化
- **百度 AI** - 菜品图像识别
- **DeepSeek AI** - 智能健康建议与食谱生成
- **HTTPX** - 异步 HTTP 客户端

## 🚀 快速开始

### 1. 创建虚拟环境

```bash
cd food-health-api
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
# 百度 AI 配置（菜品识别，可选）
BAIDU_API_KEY=your_api_key
BAIDU_SECRET_KEY=your_secret_key

# DeepSeek AI 配置（智能分析，可选）
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 数据库配置
DATABASE_URL=sqlite:///./food_health.db

# 应用配置
DEBUG=true
APP_NAME=智能食物识别健康助手
API_VERSION=v1
```

> **注意**：未配置百度 AI 时，识别接口返回模拟数据；未配置 DeepSeek 时，健康建议使用本地规则生成。

### 4. 启动服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问 API 文档

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## 📡 API 接口

### 健康检查
| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/api/v1/status` | GET | API 状态与功能检查 |

### 食物识别
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/recognize` | POST | 上传图片识别食物 |
| `/api/v1/recognize/test` | GET | 测试识别（模拟数据）|

### 食物信息
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/food/{name}` | GET | 获取食物详情 |
| `/api/v1/food` | GET | 搜索食物 |
| `/api/v1/cooking-methods` | GET | 获取烹饪方式列表 |
| `/api/v1/portions` | GET | 获取份量选项 |

### 卡路里计算
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/calculate/calories` | POST | 计算卡路里 |

### 用户管理
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/user/register` | POST | 用户注册 |
| `/api/v1/user/login` | POST | 用户登录 |
| `/api/v1/user/profile` | GET | 获取用户信息 |
| `/api/v1/user/profile` | PUT | 更新用户信息 |

### 饮食记录
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/meal/record` | POST | 添加单条饮食记录 |
| `/api/v1/meal/records/batch` | POST | 批量添加饮食记录 |
| `/api/v1/meal/record/{id}` | PUT | 更新饮食记录 |
| `/api/v1/meal/record/{id}` | DELETE | 删除饮食记录 |
| `/api/v1/meal/daily-report` | GET | 获取每日营养分析报告 |

### 健康建议
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/health/advice` | POST | 获取健康建议（AI/本地）|
| `/api/v1/health/weight` | POST | 记录体重 |
| `/api/v1/health/weight/history` | GET | 获取体重历史趋势 |
| `/api/v1/health/nutrition/history` | GET | 获取营养摄入趋势 |

### 推荐食谱
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/plans` | GET | 获取食谱列表（支持标签/来源筛选）|
| `/api/v1/plan/recommended` | GET | 获取最新推荐食谱 |
| `/api/v1/plan/generate` | POST | AI 生成个性化食谱 |
| `/api/v1/plan/{id}` | GET | 获取食谱详情 |
| `/api/v1/plan/{id}/apply` | POST | 应用食谱到每日记录 |

## 📁 项目结构

```
food-health-api/
├── app/
│   ├── main.py                 # 应用入口
│   ├── config.py               # 配置管理
│   ├── api/v1/                 # API 路由
│   │   ├── recognition.py      # 食物识别
│   │   ├── food.py             # 食物信息
│   │   ├── calories.py         # 卡路里计算
│   │   ├── user.py             # 用户管理
│   │   ├── meal.py             # 饮食记录
│   │   ├── health.py           # 健康建议
│   │   └── plan.py             # 推荐食谱
│   ├── services/               # 业务逻辑
│   │   ├── baidu_ai.py         # 百度 AI 服务
│   │   ├── deepseek_service.py # DeepSeek AI 服务
│   │   ├── food_service.py     # 食物服务
│   │   ├── meal_service.py     # 饮食记录服务
│   │   ├── user_service.py     # 用户服务
│   │   ├── calorie_calculator.py # 卡路里计算
│   │   ├── plan_profile.py     # 食谱档案构建
│   │   └── plan_recommendation.py # 食谱推荐
│   ├── models/                 # 数据库模型
│   │   ├── food.py             # 食物模型
│   │   ├── user.py             # 用户模型
│   │   ├── user_meal.py        # 饮食记录模型
│   │   ├── diet_plan.py        # 食谱计划模型
│   │   └── weight_record.py    # 体重记录模型
│   ├── schemas/                # Pydantic Schema
│   │   ├── food.py
│   │   ├── user.py
│   │   ├── meal.py
│   │   ├── health.py
│   │   └── response.py         # 统一响应格式
│   └── database/               # 数据库配置
│       ├── connection.py       # 数据库连接
│       └── init_data.py        # 初始化数据
├── tests/                      # 测试文件
├── requirements.txt            # 依赖列表
├── .env.example                # 环境变量示例
├── .gitignore
└── README.md
```

## 💡 开发说明

### 数据库初始化
- 首次启动会自动创建数据库表和初始化数据
- 包含 30+ 常见中餐菜品的营养数据
- 支持 SQLite（开发）和 MySQL（生产）

### AI 服务配置
- **百度 AI**：未配置时，识别接口返回模拟数据
- **DeepSeek AI**：未配置时，健康建议使用本地规则生成

### 响应格式
所有 API 接口统一返回格式：
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

### 用户认证
- 使用简单的 Token 认证机制
- 部分接口支持游客模式（未登录）访问

## 🔧 常用命令

```bash
# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 数据库迁移（如需）
python app/migrate_db.py

# 运行测试
pytest tests/

# 检查体重数据
python check_weight_data.py
```

## 📝 许可证

MIT License
