# -*- coding: utf-8 -*-
"""
请求频率限制配置

将 limiter 实例独立为单独模块，避免循环依赖。
各路由文件可直接 from app.rate_limit import limiter 导入使用。
"""
from slowapi import Limiter
from slowapi.util import get_remote_address


# 创建全局限流器实例（基于客户端 IP）
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],  # 全局默认：每分钟 60 次
    storage_uri="memory://",
)
