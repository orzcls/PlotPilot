"""
故事结构 API
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from application.services.story_structure_service import StoryStructureService
from infrastructure.persistence.database.story_node_repository import StoryNodeRepository
from application.paths import DATA_DIR
import os


router = APIRouter(tags=["story-structure"])


def get_service() -> StoryStructureService:
    """获取服务实例"""
    db_path = str(DATA_DIR / "aitext.db")
    repository = StoryNodeRepository(db_path)
    return StoryStructureService(repository)


class CreateNodeRequest(BaseModel):
    """创建节点请求"""
    node_type: str  # "part" | "volume" | "act"
    number: int
    title: str
    parent_id: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None


class UpdateNodeRequest(BaseModel):
    """更新节点请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    number: Optional[int] = None


class ReorderRequest(BaseModel):
    """重新排序请求"""
    node_ids: List[str]


@router.get("/novels/{novel_id}/structure")
async def get_structure_tree(
    novel_id: str,
    service: StoryStructureService = Depends(get_service)
):
    """获取小说的完整结构树"""
    try:
        return await service.get_tree(novel_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/novels/{novel_id}/structure/children")
async def get_children(
    novel_id: str,
    parent_id: Optional[str] = None,
    service: StoryStructureService = Depends(get_service)
):
    """获取子节点（用于渐进式加载）"""
    try:
        return {
            "parent_id": parent_id,
            "children": await service.get_children(novel_id, parent_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/novels/{novel_id}/structure/nodes")
async def create_node(
    novel_id: str,
    request: CreateNodeRequest,
    service: StoryStructureService = Depends(get_service)
):
    """创建节点"""
    try:
        node = await service.create_node(
            novel_id=novel_id,
            node_type=request.node_type,
            number=request.number,
            title=request.title,
            parent_id=request.parent_id,
            description=request.description,
            order_index=request.order_index
        )
        return {"success": True, "node": node}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/novels/{novel_id}/structure/nodes/{node_id}")
async def update_node(
    novel_id: str,
    node_id: str,
    request: UpdateNodeRequest,
    service: StoryStructureService = Depends(get_service)
):
    """更新节点"""
    try:
        node = await service.update_node(
            node_id=node_id,
            title=request.title,
            description=request.description,
            number=request.number
        )
        return {"success": True, "node": node}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/novels/{novel_id}/structure/nodes/{node_id}")
async def delete_node(
    novel_id: str,
    node_id: str,
    service: StoryStructureService = Depends(get_service)
):
    """删除节点"""
    try:
        success = await service.delete_node(node_id)
        if not success:
            raise HTTPException(status_code=404, detail="Node not found")
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/novels/{novel_id}/structure/reorder")
async def reorder_nodes(
    novel_id: str,
    request: ReorderRequest,
    service: StoryStructureService = Depends(get_service)
):
    """重新排序节点"""
    try:
        nodes = await service.reorder_nodes(request.node_ids)
        return {"success": True, "nodes": nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/novels/{novel_id}/structure/update-ranges")
async def update_chapter_ranges(
    novel_id: str,
    service: StoryStructureService = Depends(get_service)
):
    """更新章节范围"""
    try:
        await service.update_chapter_ranges(novel_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/novels/{novel_id}/structure/create-default")
async def create_default_structure(
    novel_id: str,
    total_chapters: int = 100,
    service: StoryStructureService = Depends(get_service)
):
    """创建默认结构"""
    try:
        result = await service.create_default_structure(novel_id, total_chapters)
        return {"success": True, "structure": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
