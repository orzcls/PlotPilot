"""FileForeshadowingRepository 集成测试"""
import pytest
import tempfile
import shutil
from pathlib import Path
from domain.novel.entities.foreshadowing_registry import ForeshadowingRegistry
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.foreshadowing import (
    Foreshadowing,
    ForeshadowingStatus,
    ImportanceLevel
)
from infrastructure.persistence.storage.file_storage import FileStorage
from infrastructure.persistence.repositories.file_foreshadowing_repository import FileForeshadowingRepository


class TestFileForeshadowingRepository:
    """FileForeshadowingRepository 集成测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp_path = tempfile.mkdtemp()
        yield Path(temp_path)
        shutil.rmtree(temp_path)

    @pytest.fixture
    def storage(self, temp_dir):
        """创建 FileStorage 实例"""
        return FileStorage(temp_dir)

    @pytest.fixture
    def repository(self, storage):
        """创建 FileForeshadowingRepository 实例"""
        return FileForeshadowingRepository(storage)

    def test_save_and_get(self, repository):
        """测试保存和获取伏笔注册表"""
        novel_id = NovelId("test-novel")
        registry = ForeshadowingRegistry(
            id="registry-1",
            novel_id=novel_id
        )

        foreshadowing = Foreshadowing(
            id="foreshadow-1",
            planted_in_chapter=1,
            description="神秘的预言",
            importance=ImportanceLevel.HIGH,
            status=ForeshadowingStatus.PLANTED,
            suggested_resolve_chapter=10
        )
        registry.register(foreshadowing)

        repository.save(registry)
        retrieved = repository.get_by_novel_id(novel_id)

        assert retrieved is not None
        assert retrieved.id == "registry-1"
        assert retrieved.novel_id.value == "test-novel"
        assert len(retrieved.foreshadowings) == 1
        assert retrieved.foreshadowings[0].description == "神秘的预言"

    def test_get_nonexistent(self, repository):
        """测试获取不存在的伏笔注册表"""
        result = repository.get_by_novel_id(NovelId("nonexistent"))
        assert result is None

    def test_delete(self, repository):
        """测试删除伏笔注册表"""
        novel_id = NovelId("test-novel")
        registry = ForeshadowingRegistry(
            id="registry-1",
            novel_id=novel_id
        )

        repository.save(registry)
        assert repository.get_by_novel_id(novel_id) is not None

        repository.delete(novel_id)
        assert repository.get_by_novel_id(novel_id) is None

    def test_save_with_multiple_foreshadowings(self, repository):
        """测试保存包含多个伏笔的注册表"""
        novel_id = NovelId("test-novel")
        registry = ForeshadowingRegistry(
            id="registry-1",
            novel_id=novel_id
        )

        registry.register(Foreshadowing(
            id="foreshadow-1",
            planted_in_chapter=1,
            description="第一个伏笔",
            importance=ImportanceLevel.HIGH,
            status=ForeshadowingStatus.PLANTED
        ))
        registry.register(Foreshadowing(
            id="foreshadow-2",
            planted_in_chapter=3,
            description="第二个伏笔",
            importance=ImportanceLevel.MEDIUM,
            status=ForeshadowingStatus.PLANTED,
            suggested_resolve_chapter=8
        ))

        repository.save(registry)
        retrieved = repository.get_by_novel_id(novel_id)

        assert len(retrieved.foreshadowings) == 2
        assert retrieved.foreshadowings[0].id == "foreshadow-1"
        assert retrieved.foreshadowings[1].id == "foreshadow-2"

    def test_save_with_resolved_foreshadowing(self, repository):
        """测试保存包含已解决伏笔的注册表"""
        novel_id = NovelId("test-novel")
        registry = ForeshadowingRegistry(
            id="registry-1",
            novel_id=novel_id
        )

        registry.register(Foreshadowing(
            id="foreshadow-1",
            planted_in_chapter=1,
            description="已解决的伏笔",
            importance=ImportanceLevel.HIGH,
            status=ForeshadowingStatus.RESOLVED,
            resolved_in_chapter=5
        ))

        repository.save(registry)
        retrieved = repository.get_by_novel_id(novel_id)

        assert len(retrieved.foreshadowings) == 1
        assert retrieved.foreshadowings[0].status == ForeshadowingStatus.RESOLVED
        assert retrieved.foreshadowings[0].resolved_in_chapter == 5

    def test_overwrite_existing(self, repository):
        """测试覆盖已存在的伏笔注册表"""
        novel_id = NovelId("test-novel")

        # 保存第一个版本
        registry1 = ForeshadowingRegistry(id="registry-1", novel_id=novel_id)
        registry1.register(Foreshadowing(
            id="foreshadow-1",
            planted_in_chapter=1,
            description="第一版",
            importance=ImportanceLevel.LOW,
            status=ForeshadowingStatus.PLANTED
        ))
        repository.save(registry1)

        # 保存第二个版本（覆盖）
        registry2 = ForeshadowingRegistry(id="registry-2", novel_id=novel_id)
        registry2.register(Foreshadowing(
            id="foreshadow-2",
            planted_in_chapter=2,
            description="第二版",
            importance=ImportanceLevel.HIGH,
            status=ForeshadowingStatus.PLANTED
        ))
        repository.save(registry2)

        # 应该只有第二版
        retrieved = repository.get_by_novel_id(novel_id)
        assert retrieved.id == "registry-2"
        assert len(retrieved.foreshadowings) == 1
        assert retrieved.foreshadowings[0].description == "第二版"
