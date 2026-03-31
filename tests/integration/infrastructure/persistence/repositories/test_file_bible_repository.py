"""FileBibleRepository 集成测试"""
import pytest
import tempfile
import shutil
from pathlib import Path
from domain.bible.entities.bible import Bible
from domain.bible.entities.character import Character
from domain.bible.entities.world_setting import WorldSetting
from domain.bible.value_objects.character_id import CharacterId
from domain.novel.value_objects.novel_id import NovelId
from infrastructure.persistence.storage.file_storage import FileStorage
from infrastructure.persistence.repositories.file_bible_repository import FileBibleRepository


class TestFileBibleRepository:
    """FileBibleRepository 集成测试"""

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
        """创建 FileBibleRepository 实例"""
        return FileBibleRepository(storage)

    def test_save_and_get(self, repository):
        """测试保存和获取 Bible"""
        bible = Bible(
            id="test-bible",
            novel_id=NovelId("test-novel")
        )

        repository.save(bible)
        retrieved = repository.get_by_id("test-bible")

        assert retrieved is not None
        assert retrieved.id == "test-bible"
        assert retrieved.novel_id.value == "test-novel"

    def test_get_by_novel_id(self, repository):
        """测试根据小说 ID 获取 Bible"""
        bible = Bible(
            id="test-bible",
            novel_id=NovelId("test-novel")
        )

        repository.save(bible)
        retrieved = repository.get_by_novel_id(NovelId("test-novel"))

        assert retrieved is not None
        assert retrieved.id == "test-bible"
        assert retrieved.novel_id.value == "test-novel"

    def test_get_nonexistent(self, repository):
        """测试获取不存在的 Bible"""
        result = repository.get_by_id("nonexistent")
        assert result is None

    def test_delete(self, repository):
        """测试删除 Bible"""
        bible = Bible(
            id="test-bible",
            novel_id=NovelId("test-novel")
        )

        repository.save(bible)
        assert repository.exists("test-bible")

        repository.delete("test-bible")
        assert not repository.exists("test-bible")

    def test_exists(self, repository):
        """测试检查 Bible 是否存在"""
        bible_id = "test-bible"

        assert not repository.exists(bible_id)

        bible = Bible(
            id=bible_id,
            novel_id=NovelId("test-novel")
        )
        repository.save(bible)

        assert repository.exists(bible_id)

    def test_save_with_characters_and_settings(self, repository):
        """测试保存包含人物和世界设定的 Bible"""
        bible = Bible(
            id="test-bible",
            novel_id=NovelId("test-novel")
        )

        # 添加人物
        character = Character(
            id=CharacterId("char-1"),
            name="张三",
            description="主角",
            relationships=["李四的朋友"]
        )
        bible.add_character(character)

        # 添加世界设定
        setting = WorldSetting(
            id="setting-1",
            name="魔法学院",
            description="主角学习的地方",
            setting_type="location"
        )
        bible.add_world_setting(setting)

        repository.save(bible)
        retrieved = repository.get_by_id("test-bible")

        assert len(retrieved.characters) == 1
        assert retrieved.characters[0].name == "张三"
        assert retrieved.characters[0].character_id.value == "char-1"
        assert retrieved.characters[0].relationships == ["李四的朋友"]

        assert len(retrieved.world_settings) == 1
        assert retrieved.world_settings[0].name == "魔法学院"
        assert retrieved.world_settings[0].setting_type == "location"
