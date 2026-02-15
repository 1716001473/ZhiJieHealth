# 部署说明 (适配 OpenCloudOS / CentOS / Ubuntu)

本文档指导如何在云服务器上部署后端 API，主要适配 **OpenCloudOS 8** (腾讯云默认) 及 CentOS/Ubuntu 系统。

---

## 1. 准备工作

### 1.1 域名与服务器
*   **域名**：购买域名并完成 ICP 备案（国内必须，否则无法访问）。
*   **服务器**：腾讯云 Lighthouse 或 CVM（OpenCloudOS 8, CentOS 8, Ubuntu 22.04 皆可）。
*   **安全组/防火墙**（非常重要！）：
    *   **登录腾讯云控制台** -> 对应的服务器详情页 -> **防火墙** 标签页。
    *   **添加规则**：放行 `80`, `443` (HTTP/HTTPS) 和 `8000` (后端测试用) 端口。
    *   *提示：如果不做这一步，外网永远连不上你的服务器。*

### 1.2 申请 SSL 证书
*   建议在腾讯云控制台申请免费 SSL 证书（有效期 1 年）。
*   下载证书时选择 **Nginx** 格式（包含 `.pem` 或 `.crt` 文件，和 `.key` 私钥文件）。

---

## 2. 环境安装

### 2.1 安装基础软件 (Nginx & Git)

**OpenCloudOS / CentOS:**
```bash
# 1. 更新系统
sudo yum update -y

# 2. 安装 Git 和 Nginx
sudo yum install -y git nginx

# 3. 启动 Nginx 并设置开机自启
sudo systemctl start nginx
sudo systemctl enable nginx
```

**Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install -y git nginx
```

### 2.2 安装 Python 环境 (推荐 Miniconda)
系统自带 Python 可能版本较老，建议使用 **Miniconda** 来管理独立的 Python 3.9 环境。

```bash
# 1. 下载 Miniconda 安装脚本
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# 2. 运行安装 (一路回车，最后输入 yes 同意协议，再输入 yes 初始化)
bash Miniconda3-latest-Linux-x86_64.sh

# 3. 刷新环境变量 (或者关掉终端重新连一次)
source ~/.bashrc

# 4. 创建项目专用环境 (指定 python 3.9)
conda create -n food-health python=3.9 -y

# 5. 激活环境
conda activate food-health
```
*(以后每次登录，执行 `conda activate food-health` 即可进入该环境)*

---

## 3. 代码部署

### 3.1 拉取代码
```bash
# 进入推荐目录
cd /home

# 拉取代码 (如果是私有仓库，需要输入账号密码或配置 SSH Key)
git clone https://gitee.com/your-username/your-project.git
# 或者如果是上传 zip 包，则使用 unzip 解压

cd your-project
```

### 3.2 安装依赖
```bash
# 确保已激活 conda 环境
pip install -r requirements.txt
```

### 3.3 修改配置
1.  **复制配置文件**：
    ```bash
    cp food-health-api/.env.example food-health-api/.env
    ```
2.  **编辑配置** (推荐使用 `vim` 或 `nano`)：
    ```bash
    vim food-health-api/.env
    ```
3.  **关键修改项**：
    *   `DEBUG=False` (生产环境必须关)
    *   `SECRET_KEY=...` (设置一个复杂的随机字符串)
    *   `CORS_ORIGINS=https://你的域名.com` (只允许你的前端域名)

---

## 4. Nginx 配置 (HTTPS)

### 4.1 上传证书
将下载的证书文件上传到服务器，建议位置：`/etc/nginx/ssl/`。
```bash
sudo mkdir -p /etc/nginx/ssl
# 使用本地电脑终端 scp 上传，或使用 SFTP 工具 (如 FileZilla, Termius)
# scp ./your-domain.pem root@你的服务器IP:/etc/nginx/ssl/
# scp ./your-domain.key root@你的服务器IP:/etc/nginx/ssl/
```

### 4.2 配置站点
1.  **复制配置模板**：
    ```bash
    # OpenCloudOS/CentOS 的 Nginx 配置通常在 /etc/nginx/conf.d/
    sudo cp deploy/nginx/food_health.conf /etc/nginx/conf.d/
    ```
    *(如果是 Ubuntu，通常放在 `/etc/nginx/sites-enabled/`，需视情况调整)*

2.  **修改配置**：
    ```bash
    sudo vim /etc/nginx/conf.d/food_health.conf
    ```
    *   修改 `server_name` 为你的真实域名。
    *   修改 `ssl_certificate` 和 `ssl_certificate_key` 指向刚才上传的证书路径。

3.  **检查并重启**：
    ```bash
    # 检查语法
    sudo nginx -t
    
    # 重启服务
    sudo systemctl reload nginx
    ```

---

## 5. 启动后端服务

### 方式 A: 临时测试 (前台运行)
```bash
cd food-health-api
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
*按 `Ctrl+C` 停止。如果访问报错，检查防火墙 8000 端口是否开放。*

### 方式 B: 生产运行 (后台守护) - 推荐
使用 `gunicorn` 配合 `uvicorn` 工作进程。

```bash
# 安装 gunicorn (如果 requirements.txt 里没有)
pip install gunicorn

# 后台启动
nohup gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 --access-logfile ./access.log --error-logfile ./error.log &
```
*此时后端在后台运行，Nginx 负责把外网 HTTPS 请求转发给它。*

### 方式 C: 终极方案 (Supervisor)
如果希望开机自启、崩溃自动重启，建议配置 `supervisord`。
1. `yum install supervisor`
2. 在 `/etc/supervisord.d/` 下创建 `.ini` 配置文件。
