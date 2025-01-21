# Webhook Email Sender

一个基于 FastAPI 的高性能异步 Webhook 服务，用于通过 SMTP 发送电子邮件。

## 功能

- 接收 GET 和 POST 请求作为 Webhook 触发器
- 发送纯文本或 HTML 格式的电子邮件
- 配置灵活，支持多种 SMTP 服务器
- 异步处理，提高性能和响应速度

## 目录

- [Webhook Email Sender](#webhook-email-sender)
  - [功能](#功能)
  - [目录](#目录)
  - [部署服务](#部署服务)
    - [从二进制文件部署](#从二进制文件部署)
      - [先决条件](#先决条件)
      - [下载分发的二进制文件](#下载分发的二进制文件)
    - [从源码部署](#从源码部署)
      - [先决条件](#先决条件-1)
      - [安装](#安装)
  - [配置](#配置)
  - [运行](#运行)
    - [从二进制文件运行](#从二进制文件运行)
    - [从源码运行](#从源码运行)
  - [使用](#使用)
    - [发送 GET 请求](#发送-get-请求)
      - [查询参数](#查询参数)
    - [发送 POST 请求](#发送-post-请求)
      - [JSON 参数](#json-参数)
      - [Header 要求](#header-要求)
  - [故障排除](#故障排除)

## 部署服务

你可以选择 [从二进制文件部署](#从二进制文件部署) 或 [从源码部署](#从源码部署)

### 从二进制文件部署

#### 先决条件

- SMTP 服务器账号（如 Gmail, QQ 邮箱等）

#### 下载分发的二进制文件

从 [Releases](https://github.com/HowieHz/webhook-email-sender/releases) 页面下载最新二进制文件即可

### 从源码部署

#### 先决条件

- Python 3.8+
- SMTP 服务器账号（如 Gmail, QQ 邮箱等）

#### 安装

1. **克隆仓库**

   ```bash
   git clone https://github.com/HowieHz/webhook-email-sender.git
   cd webhook-email-sender
   ```

2. **创建并激活虚拟环境**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

## 配置

编辑 config.json 文件，填写你的 SMTP 服务器信息和服务配置。

```json
{
  "SMTP_SERVER": "smtp.example.com",
  "SMTP_PORT": 587,
  "SMTP_TLS": false,
  "SMTP_USERNAME": "your_username",
  "SMTP_PASSWORD_ENV": "SMTP_PASSWORD",
  "SMTP_PASSWORD": "your_password",
  "SERVICE_HOST": "127.0.0.1",
  "SERVICE_PORT": 5000,
  "SERVICE_PATH": "/webhook",
  "SERVICE_TOKEN": ""
}
```

- **SMTP_SERVER**: SMTP 服务器地址
- **SMTP_PORT**: SMTP 服务器端口
- **SMTP_TLS**: 是否启用 TLS 加密
- **SMTP_USERNAME**: SMTP 登录用户名
- **SMTP_PASSWORD_ENV**: 存储 SMTP 密码的环境变量名称
- **SMTP_PASSWORD**: SMTP 登录密码（如果未设置环境变量）
- **SERVICE_HOST**: 服务监听的主机
- **SERVICE_PORT**: 服务监听的端口
- **SERVICE_PATH**: Webhook 路径
- **SERVICE_TOKEN**: 用于身份验证的令牌，如果置空则为不启用

> **解释**：程序会先读取配置文件 **SMTP_PASSWORD_ENV** 项所指定的环境变量，如果指定的环境变量未设置，则会读取配置文件的 **SMTP_PASSWORD**  项作为密码。

> **注意**: 为了安全起见，不要将 config.json 传到公共代码仓库。

## 运行

### 从二进制文件运行

直接运行下载的二进制文件即可启动服务

### 从源码运行

使用以下命令启动服务：

```bash
python main.py
```

或者使用 uvicorn 直接运行：

```bash
uvicorn main:app --host 127.0.0.1 --port 5000
```

服务将监听配置文件中指定的主机和端口。

## 使用

### 发送 GET 请求

发送带查询参数的 GET 请求以触发邮件发送。

#### 查询参数

- **to**: 收件人的电子邮件地址（必需）
- **subject**: 邮件主题（可选）
- **body**: 邮件正文内容（可选）
- **type**: 邮件内容的类型，"plain" 或 "html"（可选，默认为 "plain"）
- **token**: 用于身份验证的令牌（如启用则为必需项）


**示例**：

```powershell
Invoke-WebRequest -Uri "http://localhost:5000/webhook?subject=测试邮件&to=recipient@example.com&body=这是测试邮件内容" -Method GET
```

```bash
curl "http://localhost:5000/webhook?subject=测试邮件&to=recipient@example.com&body=这是测试邮件内容"
```

### 发送 POST 请求

发送 JSON 数据的 POST 请求以触发邮件发送。

#### JSON 参数

- **to**: 收件人的电子邮件地址（必需）
- **subject**: 邮件主题（可选）
- **body**: 邮件正文内容（可选）
- **type**: 邮件内容的类型，"plain" 或 "html"（可选，默认为 "plain"）
- **token**: 用于身份验证的令牌（如启用则为必需项）

#### Header 要求

- **Content-Type**: 必须包括 `application/json`

**PowerShell 示例**：

```powershell
$headers = @{
    "Content-Type" = "application/json; charset=utf-8"
}

$body = @{
    subject = "测试邮件"
    body    = "这是测试邮件内容"
    to      = "recipient@example.com"
    type    = "plain"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/webhook" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

**cURL 示例**：

```bash
curl -X POST "http://localhost:5000/webhook" \
     -H "Content-Type: application/json; charset=utf-8" \
     -d '{"subject": "测试邮件", "body": "这是测试邮件内容", "to": "recipient@example.com", "type": "plain"}'
```

## 故障排除

- **配置文件未找到**: 确保 config.json 存在于项目根目录，并且包含所有必需的字段。
- **SMTP 连接失败**: 检查 SMTP 服务器地址、端口、用户名和密码是否正确。确保网络允许与 SMTP 服务器的连接。
- **邮件发送失败**: 查看服务器日志中的错误信息，确保 SMTP 配置正确，并且目标邮箱地址有效。
