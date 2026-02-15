# -*- coding: utf-8 -*-
"""
用户服务
"""
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.models.user import User, RecognitionHistory
from app.schemas.user import (
    UserRegisterRequest, UserResponse, HistoryItemResponse
)
from app.config import get_settings

settings = get_settings()

from passlib.context import CryptContext

# 配置密码哈希上下文，使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """密码哈希（使用 bcrypt）"""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证密码
    兼容旧的 SHA256 哈希（无缝迁移）
    """
    # 1. 检查是否为旧的 SHA256 哈希 (64位 hex 字符串，且不包含 $ 分隔符)
    if len(password_hash) == 64 and "$" not in password_hash:
        # 手动验证旧哈希
        is_valid = hashlib.sha256(password.encode()).hexdigest() == password_hash
        return is_valid

    # 2. 验证 bcrypt 哈希
    return pwd_context.verify(password, password_hash)


ALGORITHM = "HS256"


def generate_token(user_id: int) -> str:
    """生成标准 JWT 访问令牌"""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.access_token_expire_days)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[int]:
    """验证令牌，返回 user_id"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except JWTError:
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
        
        # 自动迁移：如果是旧的 SHA256 哈希，登录成功后自动升级为 bcrypt
        if len(user.password_hash) == 64 and "$" not in user.password_hash:
            user.password_hash = hash_password(password)
            self.db.commit()
            
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
            weight=user.weight,
            height=user.height,
            age=user.age,
            gender=user.gender,
            activity=user.activity,
            health_conditions=user.get_health_conditions_list(),
            allergies=user.get_allergies_list(),
            health_goal=user.health_goal,
            dietary_preferences=user.dietary_preferences,
            created_at=user.created_at,
        )

    def get_user_by_openid(self, openid: str) -> Optional[User]:
        """根据 OpenID 获取用户"""
        return self.db.query(User).filter(User.openid == openid).first()

    def create_wechat_user(self, openid: str, unionid: Optional[str] = None, user_info: Optional[dict] = None) -> User:
        """创建微信用户"""
        import uuid
        # 生成随机用户名和密码
        random_suffix = uuid.uuid4().hex[:8]
        username = f"wx_{random_suffix}"
        password = uuid.uuid4().hex
        
        nickname = user_info.get("nickName") if user_info else f"用户_{random_suffix[:4]}"
        avatar_url = user_info.get("avatarUrl") if user_info else None

        user = User(
            username=username,
            password_hash=hash_password(password),
            nickname=nickname,
            avatar_url=avatar_url,
            openid=openid,
            unionid=unionid
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


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
