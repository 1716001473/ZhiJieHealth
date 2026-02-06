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
    debug: bool = True
    
    # 数据库配置
    database_url: str = "sqlite:///./food_health.db"
    
    # 百度AI配置
    baidu_api_key: str = ""
    baidu_secret_key: str = ""
    
    # DeepSeek AI 配置
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # 安全配置
    secret_key: str = "food_health_secret_key_2026"

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


@lru_cache()
def get_settings() -> Settings:
    """
    获取配置单例
    使用 lru_cache 确保配置只加载一次
    """
    return Settings()
