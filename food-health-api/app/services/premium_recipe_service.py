# -*- coding: utf-8 -*-
"""
精品食谱服务层
"""
import json
import logging
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.food import PremiumRecipe
from app.schemas.premium_recipe import (
    PremiumRecipeCreate,
    PremiumRecipeUpdate,
    PremiumRecipeResponse,
)

logger = logging.getLogger(__name__)


class PremiumRecipeService:
    """精品食谱服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_list(
        self,
        page: int = 1,
        page_size: int = 10,
        category: Optional[str] = None,
        tag: Optional[str] = None,
        is_featured: Optional[bool] = None,
        keyword: Optional[str] = None,
    ) -> Tuple[List[PremiumRecipe], int]:
        """
        获取精品食谱列表
        
        Args:
            page: 页码
            page_size: 每页数量
            category: 分类筛选
            tag: 标签筛选
            is_featured: 是否只显示精选
            keyword: 搜索关键词
            
        Returns:
            (食谱列表, 总数)
        """
        query = self.db.query(PremiumRecipe).filter(PremiumRecipe.is_active == True)
        
        if category:
            query = query.filter(PremiumRecipe.category == category)
        
        if tag:
            # JSON 字符串中包含标签
            query = query.filter(PremiumRecipe.tags.like(f'%"{tag}"%'))
        
        if is_featured is not None:
            query = query.filter(PremiumRecipe.is_featured == is_featured)
        
        if keyword:
            query = query.filter(
                PremiumRecipe.name.like(f"%{keyword}%") |
                PremiumRecipe.description.like(f"%{keyword}%")
            )
        
        # 计算总数
        total = query.count()
        
        # 排序和分页
        recipes = (
            query
            .order_by(PremiumRecipe.is_featured.desc())
            .order_by(PremiumRecipe.sort_order.desc())
            .order_by(PremiumRecipe.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        
        return recipes, total
    
    def get_by_id(self, recipe_id: int) -> Optional[PremiumRecipe]:
        """根据ID获取食谱"""
        return self.db.query(PremiumRecipe).filter(PremiumRecipe.id == recipe_id).first()
    
    def get_by_name(self, name: str) -> Optional[PremiumRecipe]:
        """根据名称获取食谱"""
        return self.db.query(PremiumRecipe).filter(PremiumRecipe.name == name).first()
    
    def create(self, recipe_data: PremiumRecipeCreate) -> PremiumRecipe:
        """创建精品食谱"""
        # 准备数据
        data = recipe_data.model_dump()
        
        # 将列表转为 JSON 字符串
        if data.get("tags"):
            data["tags"] = json.dumps(data["tags"], ensure_ascii=False)
        if data.get("ingredients"):
            data["ingredients"] = json.dumps(
                [item.model_dump() if hasattr(item, 'model_dump') else item for item in data["ingredients"]],
                ensure_ascii=False
            )
        if data.get("steps"):
            data["steps"] = json.dumps(
                [item.model_dump() if hasattr(item, 'model_dump') else item for item in data["steps"]],
                ensure_ascii=False
            )
        
        recipe = PremiumRecipe(**data)
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        
        logger.info(f"✅ 创建精品食谱: {recipe.name}")
        return recipe
    
    def update(self, recipe_id: int, recipe_data: PremiumRecipeUpdate) -> Optional[PremiumRecipe]:
        """更新精品食谱"""
        recipe = self.get_by_id(recipe_id)
        if not recipe:
            return None
        
        # 只更新非 None 的字段
        update_data = recipe_data.model_dump(exclude_unset=True)
        
        # 将列表转为 JSON 字符串
        if "tags" in update_data and update_data["tags"] is not None:
            update_data["tags"] = json.dumps(update_data["tags"], ensure_ascii=False)
        if "ingredients" in update_data and update_data["ingredients"] is not None:
            update_data["ingredients"] = json.dumps(
                [item.model_dump() if hasattr(item, 'model_dump') else item for item in update_data["ingredients"]],
                ensure_ascii=False
            )
        if "steps" in update_data and update_data["steps"] is not None:
            update_data["steps"] = json.dumps(
                [item.model_dump() if hasattr(item, 'model_dump') else item for item in update_data["steps"]],
                ensure_ascii=False
            )
        
        for key, value in update_data.items():
            setattr(recipe, key, value)
        
        self.db.commit()
        self.db.refresh(recipe)
        
        logger.info(f"✅ 更新精品食谱: {recipe.name}")
        return recipe
    
    def delete(self, recipe_id: int) -> bool:
        """删除精品食谱"""
        recipe = self.get_by_id(recipe_id)
        if not recipe:
            return False
        
        self.db.delete(recipe)
        self.db.commit()
        
        logger.info(f"🗑️ 删除精品食谱: {recipe.name}")
        return True
    
    def increment_view_count(self, recipe_id: int) -> None:
        """增加浏览数"""
        self.db.query(PremiumRecipe).filter(
            PremiumRecipe.id == recipe_id
        ).update(
            {"view_count": PremiumRecipe.view_count + 1}
        )
        self.db.commit()
    
    def toggle_favorite(self, recipe_id: int, increment: bool = True) -> None:
        """切换收藏状态（增加/减少收藏数）"""
        if increment:
            self.db.query(PremiumRecipe).filter(
                PremiumRecipe.id == recipe_id
            ).update(
                {"favorite_count": PremiumRecipe.favorite_count + 1}
            )
        else:
            self.db.query(PremiumRecipe).filter(
                PremiumRecipe.id == recipe_id,
                PremiumRecipe.favorite_count > 0
            ).update(
                {"favorite_count": PremiumRecipe.favorite_count - 1}
            )
        self.db.commit()
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        result = (
            self.db.query(PremiumRecipe.category)
            .filter(PremiumRecipe.is_active == True)
            .filter(PremiumRecipe.category.isnot(None))
            .distinct()
            .all()
        )
        return [r[0] for r in result if r[0]]
    
    def get_tags(self) -> List[str]:
        """获取所有标签（从 JSON 中提取）"""
        recipes = (
            self.db.query(PremiumRecipe.tags)
            .filter(PremiumRecipe.is_active == True)
            .filter(PremiumRecipe.tags.isnot(None))
            .all()
        )
        
        all_tags = set()
        for (tags_json,) in recipes:
            if tags_json:
                try:
                    tags = json.loads(tags_json)
                    all_tags.update(tags)
                except json.JSONDecodeError:
                    pass
        
        return sorted(list(all_tags))
    
    def get_featured(self, limit: int = 6) -> List[PremiumRecipe]:
        """获取精选食谱"""
        return (
            self.db.query(PremiumRecipe)
            .filter(PremiumRecipe.is_active == True)
            .filter(PremiumRecipe.is_featured == True)
            .order_by(PremiumRecipe.sort_order.desc())
            .limit(limit)
            .all()
        )
