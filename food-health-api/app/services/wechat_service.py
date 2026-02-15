# -*- coding: utf-8 -*-
"""
微信小程序服务
处理登录凭证校验 (code2Session) 和内容安全检测
"""
import httpx
import logging
from typing import Optional, Dict, Any, Tuple
from app.config import get_settings

logger = logging.getLogger(__name__)

class WeChatService:
    def __init__(self):
        self.settings = get_settings()
        self.app_id = self.settings.wechat_app_id
        self.app_secret = self.settings.wechat_app_secret
        self.base_url = "https://api.weixin.qq.com"
        
        if not self.app_id or not self.app_secret:
            logger.warning("⚠️ 微信 AppID 或 Secret 未配置，微信相关功能将不可用")

    async def code_to_session(self, code: str) -> Optional[Dict[str, Any]]:
        """
        凭证校验：换取 openid 和 session_key
        https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html
        """
        if not self.app_id or not self.app_secret:
            return None

        url = f"{self.base_url}/sns/jscode2session"
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "js_code": code,
            "grant_type": "authorization_code"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10.0)
                data = response.json()
                
                if data.get("errcode", 0) != 0:
                    logger.error(f"微信登录失败: {data}")
                    return None
                
                return data
        except Exception as e:
            logger.error(f"微信 API 请求异常: {e}")
            return None

    async def get_access_token(self) -> Optional[str]:
        """
        获取接口调用凭证 access_token (client_credential)
        注意：生产环境应缓存 token (有效期 2小时)
        这里简化为每次请求（实际项目中请务必添加 Redis 缓存）
        """
        if not self.app_id or not self.app_secret:
            return None
            
        url = f"{self.base_url}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=5.0)
                data = response.json()
                
                if data.get("errcode", 0) != 0:
                    logger.error(f"获取 AccessToken 失败: {data}")
                    return None
                    
                return data.get("access_token")
        except Exception as e:
            logger.error(f"AccessToken 请求异常: {e}")
            return None

    async def msg_sec_check(self, content: str, openid: str) -> bool:
        """
        文本内容安全识别 (msg_sec_check)
        https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/sec-center/sec-check/msgSecCheck.html
        
        :return: True (合规), False (违规/错误)
        """
        logger.info(f"正在进行内容安全检测: content='{content}', openid='{openid}'")

        # DEBUG: 本地强制拦截敏感词（优先于微信接口执行，便于测试）
        if "色情" in content or "测试" in content:
            logger.warning(f"本地强制拦截敏感词: {content}")
            return False

        # 没有配置微信，默认通过（开发与测试便利）
        if not self.app_id:
            logger.warning("未配置 WECHAT_APP_ID，跳过微信内容安全检测")
            return True
            
        token = await self.get_access_token()
        if not token:
            logger.error("内容安全检测失败: 无法获取 AccessToken")
            # 获取不到 token，视为检测失败（安全起见）
            return False

        url = f"{self.base_url}/wxa/msg_sec_check?access_token={token}"
        
        payload = {
            "content": content,
            "version": 2,
            "scene": 2, # 场景枚举值（1 资料；2 评论；3 论坛；4 社交日志）
            "openid": openid
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=5.0)
                data = response.json()
                
                logger.info(f"微信内容安全响应: {data}")
                
                # result.suggest: 'pass' | 'risky' | 'review'
                if data.get("errcode", 0) == 0:
                    if data.get("result", {}).get("suggest") == "pass":
                        return True
                    else:
                        logger.warning(f"内容安全拦截: {content[:10]}... -> {data}")
                        return False
                else:
                    logger.error(f"内容安全接口报错: {data}")
                    # 接口报错时，是否放行视业务紧迫性而定，这里暂定为不通过
                    return False
        except Exception as e:
            logger.error(f"内容安全请求异常: {e}")
            return False

wechat_service = WeChatService()
