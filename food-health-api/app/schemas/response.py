# -*- coding: utf-8 -*-
"""
通用响应结构
"""
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """通用 API 响应结构"""
    model_config = ConfigDict(from_attributes=True)

    code: int = 0
    message: str = "success"
    data: Optional[T] = None

    @classmethod
    def success(cls, data: Any = None, message: str = "success") -> dict:
        """成功响应 - 返回纯 dict，避免 Pydantic Generic 序列化问题"""
        return {
            "code": 0,
            "message": message,
            "data": _serialize(data),
        }

    @classmethod
    def error(cls, code: int = -1, message: str = "error") -> dict:
        """错误响应"""
        return {
            "code": code,
            "message": message,
            "data": None,
        }


def _serialize(obj: Any) -> Any:
    """递归将 Pydantic 模型转为可 JSON 序列化的 dict/list"""
    if obj is None:
        return None
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    return obj
