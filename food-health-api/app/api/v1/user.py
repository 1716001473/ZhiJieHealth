# -*- coding: utf-8 -*-
"""
用户 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, File, UploadFile, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.user_service import UserService, HistoryService, generate_token
from app.schemas.response import APIResponse
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserLoginResponse,
    UserResponse, UserUpdateRequest,
    HistoryListResponse, HistoryItemResponse, SaveHistoryRequest,
    ChangePasswordRequest, AvatarUploadRequest, AvatarUploadResponse,
    WeChatLoginRequest
)
from app.config import get_settings
from app.rate_limit import limiter

router = APIRouter()
settings = get_settings()


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[int]:
    """获取当前用户 ID（从 token 中）"""
    if not authorization:
        return None
    
    # 支持 "Bearer token" 格式
    token = authorization.replace("Bearer ", "").strip()
    if not token:
        return None
    
    user_service = UserService(db)
    user = user_service.get_user_by_token(token)
    return user.id if user else None


def require_login(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> int:
    """要求登录，返回用户 ID"""
    user_id = get_current_user(authorization, db)
    if not user_id:
        raise HTTPException(status_code=401, detail="请先登录")
    return user_id


def optional_login(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[int]:
    """可选登录，返回用户 ID"""
    return get_current_user(authorization, db)


@router.post("/user/register", response_model=APIResponse[UserResponse])
@limiter.limit("3/minute")  # 注册接口：每分钟最多 3 次
async def register(
    request_body: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    用户注册
    
    - **username**: 用户名（3-50字符）
    - **password**: 密码（6位以上）
    - **nickname**: 昵称（可选）
    """
    user_service = UserService(db)
    user = user_service.register(request_body)
    
    if not user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    return APIResponse.success(
        data=user_service.to_response(user),
        message="注册成功"
    )


@router.post("/user/login", response_model=APIResponse[UserLoginResponse])
@limiter.limit("5/minute")  # 登录接口：每分钟最多 5 次（防暂力破解）
async def login(
    request_body: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    用户登录
    
    返回访问令牌，后续请求需在 Header 中携带：
    `Authorization: Bearer <token>`
    """
    user_service = UserService(db)
    user = user_service.login(request_body.username, request_body.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    token = generate_token(user.id)
    
    return APIResponse.success(
        data=UserLoginResponse(
            user=user_service.to_response(user),
            token=token
        ),
        message="登录成功"
    )


@router.post("/user/wechat-login", response_model=APIResponse[UserLoginResponse])
async def wechat_login(
    request_body: WeChatLoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    微信小程序一键登录
    
    接收 code，换取 openid，自动注册或登录
    """
    from app.services.wechat_service import wechat_service
    
    # 1. code 换取 openid
    wx_session = await wechat_service.code_to_session(request_body.code)
    if not wx_session or "openid" not in wx_session:
        raise HTTPException(status_code=400, detail="微信登录失败，无法获取 OpenID")
    
    openid = wx_session["openid"]
    unionid = wx_session.get("unionid")
    
    # 2. 查找或创建用户
    user_service = UserService(db)
    user = user_service.get_user_by_openid(openid)
    
    is_new_user = False
    if not user:
        # 自动注册
        user = user_service.create_wechat_user(
            openid=openid, 
            unionid=unionid,
            user_info=request_body.userInfo
        )
        is_new_user = True
    elif request_body.userInfo:
        # 更新用户信息（如果提供了且用户未设置头像昵称）
        # 这里可以根据业务需求决定是否覆盖
        pass

    # 3. 生成 token
    token = generate_token(user.id)
    
    return APIResponse.success(
        data=UserLoginResponse(
            user=user_service.to_response(user),
            token=token
        ),
        message="注册成功" if is_new_user else "登录成功"
    )


@router.get("/user/profile", response_model=APIResponse[UserResponse])
async def get_profile(
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """获取当前用户信息"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return APIResponse.success(data=user_service.to_response(user))


@router.put("/user/profile", response_model=APIResponse[UserResponse])
async def update_profile(
    request: UserUpdateRequest,
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """更新用户信息"""
    user_service = UserService(db)
    # 1. 内容安全检测 (昵称)
    if request.nickname:
        from app.services.wechat_service import wechat_service
        # 获取当前用户 openid
        user_check = user_service.get_user_by_id(user_id)
        if user_check and user_check.openid:
            # 必须 await 异步方法
            is_valid = await wechat_service.msg_sec_check(request.nickname, user_check.openid)
            if not is_valid:
                raise HTTPException(status_code=400, detail="昵称包含违规内容，请修改")

    user = user_service.update_user(
        user_id,
        nickname=request.nickname,
        avatar_url=request.avatar_url,
        health_conditions=request.health_conditions,
        allergies=request.allergies,
        health_goal=request.health_goal,
        dietary_preferences=request.dietary_preferences,
    )
    
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return APIResponse.success(
        data=user_service.to_response(user),
        message="更新成功"
    )


# ========== 识别历史 ==========

@router.get("/history", response_model=APIResponse[HistoryListResponse])
async def get_history(
    page: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = Depends(optional_login),
    db: Session = Depends(get_db),
):
    """获取识别历史"""
    if not user_id:
        if settings.allow_guest_history:
            return APIResponse.success(data=HistoryListResponse(total=0, items=[]))
        raise HTTPException(status_code=401, detail="请先登录")
    history_service = HistoryService(db)
    items, total = history_service.get_user_history(user_id, page, page_size)
    
    return APIResponse.success(data=HistoryListResponse(
        total=total,
        items=[history_service.to_response(item) for item in items]
    ))


@router.post("/history", response_model=APIResponse[HistoryItemResponse])
async def save_history(
    request: SaveHistoryRequest,
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """保存识别历史"""
    history_service = HistoryService(db)
    # 1. 内容安全检测 (备注)
    if request.note:
        from app.services.wechat_service import wechat_service
        # 获取当前用户 openid
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        if user and user.openid:
            # 必须 await 异步方法
            is_valid = await wechat_service.msg_sec_check(request.note, user.openid)
            if not is_valid:
                raise HTTPException(status_code=400, detail="备注包含违规内容，请修改")

    history = history_service.save_history(
        user_id=user_id,
        recognized_food=request.recognized_food,
        confidence=request.confidence,
        selected_portion=request.selected_portion,
        selected_cooking=request.selected_cooking,
        final_calories_min=request.final_calories_min,
        final_calories_max=request.final_calories_max,
        result_data=request.result_data,
        meal_type=request.meal_type,
        note=request.note,
    )
    
    return APIResponse.success(
        data=history_service.to_response(history),
        message="保存成功"
    )


@router.delete("/history/{history_id}", response_model=APIResponse)
async def delete_history(
    history_id: int,
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """删除识别历史"""
    history_service = HistoryService(db)
    success = history_service.delete_history(user_id, history_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return APIResponse.success(message="删除成功")


# ========== 头像上传 ==========

@router.post("/user/avatar", response_model=APIResponse[AvatarUploadResponse])
async def upload_avatar(
    request: AvatarUploadRequest,
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """
    上传头像 (Base64 方式)

    接收 Base64 编码的图片，保存后返回头像 URL
    """
    import base64
    import uuid
    from pathlib import Path

    # 解析 Base64 图片
    try:
        # 支持 data:image/xxx;base64, 前缀
        image_data = request.image_base64
        if "," in image_data:
            image_data = image_data.split(",")[1]

        image_bytes = base64.b64decode(image_data)
    except Exception:
        raise HTTPException(status_code=400, detail="图片格式错误")

    # 限制图片大小 (2MB)
    if len(image_bytes) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 2MB")

    # 创建存储目录
    avatar_dir = Path("static/avatars")
    avatar_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    filename = f"{user_id}_{uuid.uuid4().hex[:8]}.jpg"
    filepath = avatar_dir / filename

    # 保存图片
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    # 生成 URL
    avatar_url = f"/static/avatars/{filename}"

    # 更新用户头像
    user_service = UserService(db)
    user_service.update_user(user_id, avatar_url=avatar_url)

    return APIResponse.success(
        data=AvatarUploadResponse(avatar_url=avatar_url),
        message="头像上传成功"
    )


@router.post("/user/avatar/upload", response_model=APIResponse[AvatarUploadResponse])
async def upload_avatar_file(
    file: UploadFile = File(...),
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """
    上传头像 (文件方式)

    接收文件上传，保存后返回头像 URL
    适用于 uni.uploadFile 等文件上传方式
    """
    import uuid
    from pathlib import Path

    # 读取文件内容
    try:
        image_bytes = await file.read()
    except Exception:
        raise HTTPException(status_code=400, detail="文件读取失败")

    # 限制图片大小 (2MB)
    if len(image_bytes) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="图片大小不能超过 2MB")

    # 创建存储目录
    avatar_dir = Path("static/avatars")
    avatar_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件名
    ext = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{user_id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = avatar_dir / filename

    # 保存图片
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    # 生成 URL
    avatar_url = f"/static/avatars/{filename}"

    # 更新用户头像
    user_service = UserService(db)
    user_service.update_user(user_id, avatar_url=avatar_url)

    return APIResponse.success(
        data=AvatarUploadResponse(avatar_url=avatar_url),
        message="头像上传成功"
    )


# ========== 修改密码 ==========

@router.put("/user/password", response_model=APIResponse)
@limiter.limit("5/minute")  # 修改密码接口：每分钟最多 5 次
async def change_password(
    request_body: ChangePasswordRequest,
    request: Request,
    user_id: int = Depends(require_login),
    db: Session = Depends(get_db),
):
    """
    修改密码

    需要验证旧密码后才能设置新密码
    """
    from app.services.user_service import verify_password, hash_password

    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 验证旧密码
    if not verify_password(request_body.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="旧密码错误")

    # 更新密码
    user.password_hash = hash_password(request_body.new_password)
    db.commit()

    return APIResponse.success(message="密码修改成功")
