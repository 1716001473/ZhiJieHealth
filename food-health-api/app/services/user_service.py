# -*- coding: utf-8 -*-
"""
用户服务
"""
import hashlib
import hmac
import json
import base64
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User, RecognitionHistory
from app.schemas.user import (
    UserRegisterRequest, UserResponse, HistoryItemResponse
)
from app.config import get_settings

settings = get_settings()

def hash_password(password: str) -> str:
    """密码哈希（简单实现，生产环境用 bcrypt）"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return hash_password(password) == password_hash


def _base64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def _base64_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)


def generate_token(user_id: int) -> str:
    """生成无状态访问令牌 (HMAC签名)"""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + settings.access_token_expire_days * 24 * 3600,
        "iat": int(time.time())
    }
    
    header_b64 = _base64_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = _base64_encode(json.dumps(payload).encode('utf-8'))
    
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        settings.secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    signature_b64 = _base64_encode(signature)
    
    return f"{message}.{signature_b64}"


def verify_token(token: str) -> Optional[int]:
    """验证令牌，返回 user_id"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
            
        header_b64, payload_b64, signature_b64 = parts
        
        message = f"{header_b64}.{payload_b64}"
        expected_signature = hmac.new(
            settings.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        if not hmac.compare_digest(_base64_encode(expected_signature), signature_b64):
            return None
            
        payload = json.loads(_base64_decode(payload_b64).decode('utf-8'))
        
        # 检查过期时间
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload.get("sub")
        
    except Exception:
        return None


class UserService:
    """用户服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register(self, request: UserRegisterRequest) -> Optional[User]:
        """用户注册"""
        # 检查用户名是否已存在
        existing = self.db.query(User).filter(User.username == request.username).first()
        if existing:
            return None
        
        # 创建用户
        user = User(
            username=request.username,
            password_hash=hash_password(request.password),
            nickname=request.nickname or request.username,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def login(self, username: str, password: str) -> Optional[User]:
        """用户登录"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_token(self, token: str) -> Optional[User]:
        """根据 token 获取用户"""
        user_id = verify_token(token)
        if not user_id:
            return None
        return self.get_user_by_id(user_id)
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                if key in ["health_conditions", "allergies"] and isinstance(value, list):
                    setattr(user, key, ",".join(value))
                elif key == "dietary_preferences" and isinstance(value, list):
                    setattr(user, key, ",".join(value))
                else:
                    setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def to_response(self, user: User) -> UserResponse:
        """转换为响应对象"""
        return UserResponse(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            health_conditions=user.get_health_conditions_list(),
            allergies=user.get_allergies_list(),
            health_goal=user.health_goal,
            dietary_preferences=user.dietary_preferences,
            created_at=user.created_at,
        )


class HistoryService:
    """识别历史服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_history(self, user_id: int, **kwargs) -> RecognitionHistory:
        """保存识别历史"""
        history = RecognitionHistory(
            user_id=user_id,
            **kwargs
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
    
    def get_user_history(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> tuple[List[RecognitionHistory], int]:
        """获取用户历史记录"""
        query = self.db.query(RecognitionHistory).filter(
            RecognitionHistory.user_id == user_id
        ).order_by(RecognitionHistory.created_at.desc())
        
        total = query.count()
        items = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return items, total
    
    def delete_history(self, user_id: int, history_id: int) -> bool:
        """删除历史记录"""
        history = self.db.query(RecognitionHistory).filter(
            RecognitionHistory.id == history_id,
            RecognitionHistory.user_id == user_id
        ).first()
        
        if not history:
            return False
        
        self.db.delete(history)
        self.db.commit()
        return True
    
    def to_response(self, history: RecognitionHistory) -> HistoryItemResponse:
        """转换为响应对象"""
        return HistoryItemResponse(
            id=history.id,
            image_url=history.image_url,
            recognized_food=history.recognized_food,
            confidence=history.confidence,
            selected_portion=history.selected_portion,
            selected_cooking=history.selected_cooking,
            final_calories_min=history.final_calories_min,
            final_calories_max=history.final_calories_max,
            result_data=history.result_data,
            meal_type=history.meal_type,
            created_at=history.created_at,
        )
