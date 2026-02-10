# 🚀 部署到腾讯云 CloudBase 指南

## 📋 前置条件

1. ✅ 已有腾讯云账号
2. ✅ 已创建 CloudBase 环境
3. ✅ 已开通 MySQL 数据库

## 🔧 后端部署（FastAPI）

### 方法一：使用 Docker 部署到 Cloud Run

#### 1. 构建 Docker 镜像

```bash
cd food-health-api
docker build -t food-health-api:latest .
```

#### 2. 推送到腾讯云镜像仓库

```bash
# 登录腾讯云镜像仓库
docker login ccr.ccs.tencentyun.com

# 标记镜像
docker tag food-health-api:latest ccr.ccs.tencentyun.com/your-namespace/food-health-api:latest

# 推送镜像
docker push ccr.ccs.tencentyun.com/your-namespace/food-health-api:latest
```

#### 3. 部署到 Cloud Run

访问 CloudBase 控制台的 Cloud Run 页面：
https://tcb.cloud.tencent.com/dev?envId={你的环境ID}#/platform-run

点击"新建服务"，填写：
- **服务名称**：food-health-api
- **运行环境**：选择"自定义镜像"
- **镜像地址**：ccr.ccs.tencentyun.com/your-namespace/food-health-api:latest
- **端口**：8000
- **环境变量**：
  ```bash
  DATABASE_URL=mysql+pymysql://username:password@host:3306/food_health
  BAIDU_API_KEY=你的百度API密钥
  BAIDU_SECRET_KEY=你的百度Secret密钥
  DEEPSEEK_API_KEY=你的DeepSeek密钥
  DEEPSEEK_BASE_URL=https://api.deepseek.com
  DEBUG=false
  CORS_ORIGINS=*
  ```

#### 4. 获取后端访问地址

部署成功后，你会获得一个类似这样的地址：
```
https://xxx-service-xxx.ap-shanghai.tcb.run
```

## 🎨 前端部署（UniApp）

### 1. 修改前端 API 配置

编辑 `food-health-app/src/config.js`，修改 API_BASE_URL 为后端地址：

```javascript
export const API_BASE_URL = 'https://xxx-service-xxx.ap-shanghai.tcb.run'
```

### 2. 构建 H5 应用

```bash
cd food-health-app
npm run build:h5
```

构建完成后，静态文件在 `dist/build/h5` 目录。

### 3. 上传到 CloudBase 静态托管

#### 方法一：使用 CloudBase CLI（推荐）

```bash
# 安装 CloudBase CLI
npm install -g @cloudbase/cli

# 登录
cloudbase login

# 初始化（在项目根目录）
cd food-health-app
cloudbase init

# 部署静态网站
cloudbase hosting deploy dist/build/h5 -e 你的环境ID
```

#### 方法二：使用控制台上传

1. 访问静态网站托管页面：
   https://tcb.cloud.tencent.com/dev?envId={你的环境ID}#/static-hosting

2. 点击"新建网站"
3. 配置：
   - 网站名称：food-health-h5
   - 部署方式：上传文件夹
   - 选择：`dist/build/h5` 目录
4. 点击"部署"

### 4. 获取前端访问地址

部署成功后，你会获得类似这样的地址：
```
https://xxx.tcb.qcloud.la
```

## 📝 配置跨域

在 CloudBase 控制台配置安全域名：

1. 访问：https://tcb.cloud.tencent.com/dev?envId={你的环境ID}#/env
2. 找到"安全域名"配置
3. 添加前端域名到 CORS 白名单

## 🧪 测试部署

1. 访问前端地址
2. 测试拍照识别功能
3. 测试用户登录
4. 测试 AI 食谱生成

## 📊 数据库迁移

如果你的 SQLite 数据库有数据，需要迁移到 MySQL：

```bash
# 导出 SQLite 数据
sqlite3 food_health.db .dump > data.sql

# 导入到 MySQL
mysql -h host -u username -p food_health < data.sql
```

## 🔍 故障排查

### 后端无法启动
- 检查环境变量是否正确配置
- 检查数据库连接信息
- 查看 Cloud Run 日志

### 前端无法访问后端
- 检查 CORS 配置
- 检查 API_BASE_URL 是否正确
- 检查后端是否正常运行

### 数据库连接失败
- 检查 MySQL 是否已开通
- 检查连接字符串格式
- 检查数据库用户权限

## 📚 相关文档

- CloudBase 控制台：https://tcb.cloud.tencent.com/
- CloudBase 文档：https://docs.cloudbase.net/
- Cloud Run 文档：https://docs.cloudbase.net/cloud-run/README.html
