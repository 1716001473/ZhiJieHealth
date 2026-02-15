# -*- coding: utf-8 -*-
"""
应用配置模块
使用 pydantic-settings 管理环境变量
Updated: 2026-02-13 - 添加 secret_key 安全校验
"""
import secrets
import logging
from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# 不安全的示例密钥列表（防止用户直接复制 .env.example 不改）
_UNSAFE_SECRET_KEYS = {"", "your-secret-key", "change-me", "secret", "123456"}


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "智能食物识别健康助手"
    api_version: str = "v1"
    debug: bool = False

    # 数据库配置
    database_url: str = "sqlite:///./food_health.db"

    # 百度AI配置（备用）
    baidu_api_key: str = ""
    baidu_secret_key: str = ""

    # 豆包 AI 配置（火山引擎方舟）- 主要识别服务
    doubao_api_key: str = ""
    doubao_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    doubao_model: str = "doubao-seed-1-8-251228"
    doubao_image_model: str = "doubao-seedream-4-5-251128"

    # DeepSeek AI 配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # 安全配置（必须通过环境变量或 .env 文件设置）
    secret_key: str = ""

    # CORS 允许的来源（逗号分隔，如 "http://localhost:5173,https://example.com"）
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # FatSecret API 配置
    fatsecret_client_id: str = ""
    fatsecret_client_secret: str = ""

    # 微信小程序配置
    wechat_app_id: str = ""
    wechat_app_secret: str = ""

    # 游客模式（开发期默认开启）
    allow_guest_history: bool = True
    
    # JWT Token 过期时间（天）
    access_token_expire_days: int = 7
    
    # 模型配置，从 .env 文件读取环境变量
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def validate_security_config(self):
        """
        全量安全配置校验：
        1. SECRET_KEY 安全性检查
        2. CORS 生产环境严格检查
        """
        # 1. 校验 SECRET_KEY
        if self.secret_key.strip().lower() in _UNSAFE_SECRET_KEYS:
            if self.debug:
                # 开发模式：自动生成随机密钥，打印警告
                generated = secrets.token_urlsafe(32)
                logger.warning(
                    "⚠️ SECRET_KEY 未配置或不安全！已自动生成临时密钥。"
                    "生产环境请在 .env 中设置强随机密钥！"
                )
                self.secret_key = generated
            else:
                # 生产模式：直接拒绝启动
                raise ValueError(
                    "🚫 严重安全风险：SECRET_KEY 未配置！"
                    "请在 .env 文件中设置一个至少 32 字符的随机密钥。"
                    "可使用命令生成：python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
        elif len(self.secret_key) < 16:
            logger.warning(
                f"⚠️ SECRET_KEY 长度仅 {len(self.secret_key)} 字符，建议至少 32 字符以确保安全。"
            )

        # 2. 校验 CORS 配置 (仅生产环境)
        if not self.debug:
            origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
            if "*" in origins:
                raise ValueError(
                    "🚫 严重安全风险：生产环境 (DEBUG=False) 禁止配置 CORS_ORIGINS=*"
                    "请在 .env 中明确指定允许的前端域名，例如：https://your-domain.com"
                )
            if not origins:
                logger.warning("⚠️ 生产环境未配置 CORS_ORIGINS，前端可能无法访问 API")

        return self
    
    @property
    def cors_origins_list(self) -> list[str]:
        """获取解析后的 CORS 来源列表"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    @property
    def baidu_ai_configured(self) -> bool:
        """检查百度AI是否已配置"""
        return bool(self.baidu_api_key and self.baidu_secret_key)
    
    @property
    def deepseek_configured(self) -> bool:
        """检查DeepSeek是否已配置"""
        return bool(self.deepseek_api_key)

    @property
    def doubao_configured(self) -> bool:
        """检查豆包AI是否已配置"""
        return bool(self.doubao_api_key)

    @property
    def fatsecret_configured(self) -> bool:
        """检查FatSecret是否已配置"""
        return bool(self.fatsecret_client_id and self.fatsecret_client_secret)


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    使用 lru_cache 确保配置只加载一次
    """
    return Settings()
