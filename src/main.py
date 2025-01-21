import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Literal, TypedDict

import aiosmtplib
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

app = FastAPI()


class Config(TypedDict):
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_TLS: bool
    SMTP_USERNAME: str
    SMTP_PASSWORD_ENV: str
    SMTP_PASSWORD: str
    SERVICE_HOST: str
    SERVICE_PORT: int
    SERVICE_PATH: str
    SERVICE_TOKEN: str


default_config: Config = {
    "SMTP_SERVER": "smtp.example.com",
    "SMTP_PORT": 587,
    "SMTP_TLS": False,
    "SMTP_USERNAME": "your_username",
    "SMTP_PASSWORD_ENV": "SMTP_PASSWORD",
    "SMTP_PASSWORD": "your_password",
    "SERVICE_HOST": "127.0.0.1",
    "SERVICE_PORT": 5000,
    "SERVICE_PATH": "/webhook",
    "SERVICE_TOKEN": "",
}


# 从配置文件读取 SMTP 配置
def load_config(file_path: str) -> Config:
    """
    加载配置文件。

    参数:
        file_path (str): 配置文件路径。

    返回:
        Config: 配置字典。
    """

    required_keys = set(default_config.keys())
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as config_file:
            json.dump(default_config, config_file, ensure_ascii=False, indent=4)
        raise FileNotFoundError(f"配置文件未找到，已生成默认配置文件：{file_path}")

    with open(file_path, "r", encoding="utf-8") as config_file:
        config: Config = json.load(config_file)

    if not required_keys.issubset(config.keys()):
        missing = required_keys - config.keys()
        raise KeyError(f"缺少配置项：{', '.join(missing)}")

    return config


# 加载配置
config_path = os.path.join(os.path.dirname(__file__), "config.json")
config: Config = load_config(config_path)

SMTP_SERVER: str = config["SMTP_SERVER"]
SMTP_PORT: int = config["SMTP_PORT"]
SMTP_TLS: bool = config["SMTP_TLS"]
SMTP_USERNAME: str = config["SMTP_USERNAME"]
SMTP_PASSWORD_ENV: str = config["SMTP_PASSWORD_ENV"]
SMTP_PASSWORD: str = os.getenv(SMTP_PASSWORD_ENV, config["SMTP_PASSWORD"])
SERVICE_HOST: str = config["SERVICE_HOST"]
SERVICE_PORT: int = config["SERVICE_PORT"]
SERVICE_PATH: str = config["SERVICE_PATH"]
SERVICE_TOKEN: str = config["SERVICE_TOKEN"]
TOKEN_FLAG: bool = False
if SERVICE_TOKEN:
    TOKEN_FLAG = True


# 发送邮件函数
async def send_email(
    to_email: str,
    subject: str = "",
    body: str = "",
    msg_type: Literal["plain", "html"] = "plain",
) -> bool:
    """
    异步发送邮件，使用提供的主题、正文和收件人电子邮件地址

    Args:
        to_email (str): 收件人的电子邮件地址
        subject (str, optional): 邮件主题。默认为 ""
        body (str, optional): 邮件正文内容。默认为 ""
        msg_type (Literal[&quot;plain&quot;, &quot;html&quot;], optional): 消息类型。默认为 "plain"

    Returns:
        bool: 如果邮件发送成功返回 True，否则返回 False
    """

    msg = MIMEMultipart()
    msg["From"] = SMTP_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain" if msg_type == "plain" else "html", "utf-8"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            start_tls=SMTP_TLS,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
        )
        return True
    except Exception as e:
        print(f"Failed to send: {e}")
        return False


@app.get(SERVICE_PATH)
async def webhook_get(
    to: str,
    subject: str = "",
    body: str = "",
    type: Literal["plain", "html"] = "plain",
    token: str = "",
) -> JSONResponse:
    """
    处理传入的 webhook 以发送电子邮件

    Args:
        to (str): 收件人的电子邮件地址
        subject (str, optional): 邮件主题。默认为 ""
        body (str, optional): 邮件正文内容。默认为 ""
        type (Literal[&quot;plain&quot;, &quot;html&quot;], optional): 邮件内容的类型。默认为 "plain"
        token (str): 用于身份验证的令牌。默认为 ""

    Returns:
        JSONResponse: 指示邮件发送操作结果的 JSON 响应
    """

    if TOKEN_FLAG and token != SERVICE_TOKEN:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Token error"},
        )

    if await send_email(to_email=to, subject=subject, body=body, msg_type=type):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "Email sent successfully"},
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to send email"},
        )


@app.post(SERVICE_PATH)
async def webhook_post(request: Request) -> JSONResponse:
    """
    处理 POST 请求到 webhook 端点
    此函数处理来自请求的传入 JSON 数据，验证它，
    并根据提供的数据发送电子邮件

    预期的 JSON 负载: 参见文档

    Args:
        request (Request): 传入的 HTTP 请求

    Returns:
        JSONResponse: 指示操作结果的 JSON 响应
            - 200 OK: 如果邮件发送成功
            - 400 Bad Request: 如果 JSON 数据无效或缺少必需字段
            - 500 Internal Server Error: 如果发送邮件时出错
    """

    content_type: str | None = request.headers.get("content-type")
    if content_type is not None and "application/json" in content_type:
        try:
            data: dict[str, Any] = await request.json()
        except Exception:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Invalid JSON data"},
            )
    else:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid JSON data"},
        )

    token: str | None = data.get("token")

    if TOKEN_FLAG and token != SERVICE_TOKEN:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Token error"},
        )

    subject: str = data.get("subject", "")
    body: str = data.get("body", "")
    to_email: str | None = data.get("to")
    msg_type: Literal["plain", "html"] = data.get("type", "plain")

    if not to_email:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Missing 'to' fields"},
        )

    if await send_email(
        to_email=to_email, subject=subject, body=body, msg_type=msg_type
    ):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"status": "Email sent successfully"},
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Failed to send email"},
        )


if __name__ == "__main__":
    uvicorn.run(app, host=SERVICE_HOST, port=SERVICE_PORT)
