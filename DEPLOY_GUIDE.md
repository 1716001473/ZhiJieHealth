# 🚀 智能食物识别健康助手 - CloudBase 部署指南

> **环境 ID**: `lhins-0owkfwzy`
> **更新时间**: 2026-02-02

---

## 📋 部署清单

- [ ] 1. 开通 CloudBase MySQL 数据库
- [ ] 2. 导入数据库结构和初始数据
- [ ] 3. 构建 Docker 镜像并推送到镜像仓库
- [ ] 4. 在 Cloud Run 创建后端服务
- [ ] 5. 更新后端环境变量配置
- [ ] 6. 构建前端 H5 应用
- [ ] 7. 部署前端到静态托管
- [ ] 8. 更新前端 API 地址配置
- [ ] 9. 测试完整功能

---

## 第一步：开通 MySQL 数据库

### 1. 访问 MySQL 数据库页面

🔗 **地址**: https://tcb.cloud.tencent.com/dev?envId=lhins-0owkfwzy#/db/mysql

### 2. 开通 MySQL

1. 点击"开通 MySQL"按钮
2. 选择套餐：
   - **免费套餐**：1 核 CPU，2GB 内存（适合测试）
   - **按量付费**：根据实际使用量计费
3. 点击"立即开通"
4. 等待开通完成（约 1-2 分钟）

### 3. 获取数据库连接信息

开通后，点击"数据库详情"或"连接信息"，记录以下信息：

```
Host: 例如: xxx.mysql.tencentcdb.com
Port: 3306
Database: food_health
Username: 例如: root_xxx
Password: 例如: xxxxxxxx
```

---

## 第二步：导入数据库

### 方法一：使用控制台 SQL 窗口

1. 在 MySQL 数据库页面，点击"SQL 窗口"
2. 复制 `food-health-api/init_mysql.sql` 文件的内容
3. 粘贴到 SQL 窗口
4. 点击"执行"

### 方法二：使用 MySQL 客户端

```bash
# 使用命令行连接
mysql -h Host -P 3306 -u Username -p food_health < init_mysql.sql
```

---

## 第三步：部署后端（FastAPI）

### 3.1 构建 Docker 镜像

```powershell
cd G:\Project\HEALTH\food-health-api

# 构建镜像
docker build -t food-health-api:latest .
```

### 3.2 推送到腾讯云镜像仓库

#### 步骤 1：创建腾讯云镜像仓库

1. 访问腾讯云容器镜像服务：https://console.cloud.tencent.com/tcr2
2. 点击"新建命名空间"，填写：
   - 命名空间名称：`your-namespace`（例如：food-health-ns）
3. 创建完成后，记录你的命名空间名称

#### 步骤 2：登录镜像仓库

```powershell
# 登录腾讯云镜像仓库
docker login ccr.ccs.tencentyun.com

# 会提示输入用户名和密码
# 用户名：你的腾讯云账号 ID（在控制台可以看到）
# 密码：访问密钥（需要在腾讯云创建）
```

#### 步骤 3：创建访问密钥

1. 访问：https://console.cloud.tencent.com/cam/capi
2. 点击"新建密钥"
3. 记录 `SecretId`（用户名）和 `SecretKey`（密码）

#### 步骤 4：标记并推送镜像

```powershell
# 替换 your-namespace 为你的命名空间
docker tag food-health-api:latest ccr.ccs.tencentyun.com/your-namespace/food-health-api:latest

# 推送镜像
docker push ccr.ccs.tencentyun.com/your-namespace/food-health-api:latest
```

### 3.3 在 Cloud Run 创建服务

1. **访问 Cloud Run 页面**：
   🔗 https://tcb.cloud.tencent.com/dev?envId=lhins-0owkfwzy#/platform-run

2. **点击"新建服务"**

3. **填写基本信息**：
   - 服务名称：`food-health-api`
   - 服务类型：**容器型**
   - 镜像地址：`ccr.ccs.tencentyun.com/your-namespace/food-health-api:latest`

4. **配置端口**：
   - 端口：`8000`

5. **配置环境变量**：

将以下 JSON 配置粘贴到环境变量输入框（**记得替换数据库密码**）：

```json
{
  "DATABASE_URL": "mysql+pymysql://用户名:密码@数据库Host:3306/food_health",
  "BAIDU_API_KEY": "njk9ujXANaW4AFfFCAOVZZHP",
  "BAIDU_SECRET_KEY": "ODCuuEzXqhGpaBtWCZWI0JN9kRZuur1u",
  "DEEPSEEK_API_KEY": "sk-fc63b456e5ac4f1d9290a668f868914e",
  "DEEPSEEK_BASE_URL": "https://api.deepseek.com",
  "DEBUG": "false",
  "CORS_ORIGINS": "*"
}
```

**重要**：将 `DATABASE_URL` 中的：
- `用户名` 替换为你的 MySQL 用户名
- `密码` 替换为你的 MySQL 密码
- `数据库Host` 替换为你的 MySQL 主机地址

6. **配置资源规格**（推荐）：
   - CPU：`0.5` 核
   - 内存：`1 GB`
   - 最小实例数：`1`（减少冷启动延迟）
   - 最大实例数：`2`

7. **配置访问类型**：
   - 勾选：**公网访问（PUBLIC）**

8. **点击"部署"**

9. **等待部署完成**（约 2-3 分钟）

10. **记录后端访问地址**：
    部署成功后会显示类似：
    ```
    https://food-health-api-xxx.tcb.run
    ```
    记下这个地址，后面配置前端时需要用到。

---

## 第四步：部署前端（UniApp H5）

### 4.1 构建前端应用

```powershell
cd G:\Project\HEALTH\food-health-app

# 安装依赖（如果还没安装）
npm install

# 构建 H5 应用
npm run build:h5
```

构建完成后，静态文件在 `dist/build/h5` 目录。

### 4.2 部署到静态托管

#### 方法一：使用控制台上传（推荐新手）

1. **访问静态托管页面**：
   🔗 https://tcb.cloud.tencent.com/dev?envId=lhins-0owkfwzy#/static-hosting

2. **创建静态网站**：
   - 点击"新建网站"
   - 网站名称：`food-health-h5`
   - 部署方式：选择"上传文件夹"

3. **上传文件**：
   - 点击"选择文件夹"
   - 导航到：`G:\Project\HEALTH\food-health-app\dist\build\h5`
   - 点击"上传"

4. **等待上传完成**

5. **记录前端访问地址**：
    部署成功后会显示类似：
    ```
    https://xxx.tcb.qcloud.la
    ```

#### 方法二：使用 CloudBase CLI（推荐熟练用户）

```powershell
# 安装 CloudBase CLI
npm install -g @cloudbase/cli

# 登录（会跳转到浏览器授权）
cloudbase login

# 初始化（在项目根目录）
cd G:\Project\HEALTH
cloudbase init

# 部署静态网站
cloudbase hosting deploy food-health-app/dist/build/h5 -e lhins-0owkfwzy
```

---

## 第五步：更新前端 API 配置

### 5.1 获取后端访问地址

从 Cloud Run 控制台复制你的后端服务地址，例如：
```
https://food-health-api-xxx.tcb.run
```

### 5.2 更新前端配置

编辑 `food-health-app/src/config.js` 文件，将后端地址填入：

```javascript
// 生产环境配置
let prodBaseUrl = 'https://your-cloud-run-url.tcb.run';  // 替换为实际地址
```

### 5.3 重新构建并部署前端

```powershell
cd G:\Project\HEALTH\food-health-app
npm run build:h5

# 重新上传到静态托管
cloudbase hosting deploy dist/build/h5 -e lhins-0owkfwzy
```

---

## 第六步：测试部署

### 6.1 访问前端

1. 打开浏览器，访问前端地址：
   ```
   https://xxx.tcb.qcloud.la
   ```

2. 应该能看到应用首页

### 6.2 测试功能

测试以下功能是否正常：

- [ ] 拍照/上传图片识别食物
- [ ] 查看识别结果和营养信息
- [ ] 用户注册/登录
- [ ] 生成 AI 推荐食谱
- [ ] 查看饮食记录

### 6.3 检查后端日志

如果出现问题：

1. 访问 Cloud Run 服务详情页面
2. 查看"日志"标签页
3. 查找错误信息

---

## 🔧 故障排查

### 问题 1：后端服务无法启动

**原因**：
- 数据库连接信息错误
- 环境变量未正确配置

**解决方法**：
1. 检查环境变量中的 `DATABASE_URL` 格式
2. 确认 MySQL 用户名、密码、主机地址正确
3. 查看服务日志，查找具体错误

### 问题 2：前端无法访问后端

**原因**：
- API 地址配置错误
- CORS 未正确配置

**解决方法**：
1. 检查 `config.js` 中的 `prodBaseUrl` 是否正确
2. 确认后端环境变量中 `CORS_ORIGINS=*`
3. 打开浏览器开发者工具，查看网络请求错误

### 问题 3：图片上传失败

**原因**：
- 静态文件未正确上传
- 文件路径错误

**解决方法**：
1. 确认静态托管目录结构正确
2. 检查控制台上传日志
3. 重新上传静态文件

### 问题 4：AI 功能不工作

**原因**：
- API Key 未配置或配置错误
- API 服务异常

**解决方法**：
1. 检查环境变量中的 API Key 是否正确
2. 查看 DeepSeek 和百度 AI 控制台状态
3. 查看 Cloud Run 日志，查找 API 调用错误

---

## 📊 部署后监控

### Cloud Run 监控

访问服务详情页面，查看：
- CPU 使用率
- 内存使用率
- 请求量
- 响应时间

### MySQL 监控

访问数据库页面，查看：
- 连接数
- 查询性能
- 存储空间使用情况

### 静态托管监控

访问静态托管页面，查看：
- 访问量
- 流量统计
- 文件大小

---

## 🎉 部署完成！

部署成功后，你应该能够：

1. 通过浏览器访问前端应用
2. 使用所有核心功能
3. 用户数据实时保存到云数据库
4. AI 功能正常工作

---

## 📚 相关文档

- CloudBase 控制台：https://tcb.cloud.tencent.com/
- CloudRun 文档：https://docs.cloudbase.net/cloud-run/
- 静态托管文档：https://docs.cloudbase.net/hosting/
- MySQL 文档：https://docs.cloudbase.net/database/mysql/

## 🆘 需要帮助？

如果遇到问题，请检查：
1. CloudRun 服务日志
2. 浏览器控制台错误
3. 网络请求响应

祝你部署顺利！🚀
