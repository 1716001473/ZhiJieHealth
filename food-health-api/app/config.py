# -*- coding: utf-8 -*-
"""
配置管理模块
使用 pydantic-settings 从环境变量读取配置
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = "智能食物识别健康助手"
    api_version: str = "v1"
    debug: bool = False

    # 数据库配置
    database_url: str = "sqlite:///./food_health.db"

    # 百度AI配置
    baidu_api_key: str = ""
    baidu_secret_key: str = ""

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

    # 游客模式（开发期默认开启）
    allow_guest_history: bool = True
    
    # 模型配置，从 .env 文件读取环境变量
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    @property
    def baidu_ai_configured(self) -> bool:
        """检查百度AI是否已配置"""
        return bool(self.baidu_api_key and self.baidu_secret_key)
    
    @property
    def deepseek_configured(self) -> bool:
        """检查DeepSeek是否已配置"""
        return bool(self.deepseek_api_key)

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
