# -*- coding: utf-8 -*-
"""
通用响应结构
"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    """通用 API 响应结构"""
    model_config = ConfigDict(from_attributes=True)
    
    code: int = 0
    message: str = "success"
    data: Optional[T] = None
    
    @classmethod
    def success(cls, data: T = None, message: str = "success"):
        """成功响应"""
        return cls(code=0, message=message, data=data)
    
    @classmethod
    def error(cls, code: int = -1, message: str = "error"):
        """错误响应"""
        return cls(code=code, message=message, data=None)
