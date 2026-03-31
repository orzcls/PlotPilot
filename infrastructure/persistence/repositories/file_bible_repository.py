"""基于文件的 Bible 仓储实现"""
import logging
from typing import Optional
from domain.bible.entities.bible import Bible
from domain.bible.repositories.bible_repository import BibleRepository
from domain.novel.value_objects.novel_id import NovelId
from infrastructure.persistence.storage.backend import StorageBackend
from infrastructure.persistence.mappers.bible_mapper import BibleMapper

logger = logging.getLogger(__name__)


class FileBibleRepository(BibleRepository):
    """基于文件系统的 Bible 仓储实现

    使用 JSON 文件存储 Bible 数据。
    """

    def __init__(self, storage: StorageBackend):
        """初始化仓储

        Args:
            storage: 存储后端
        """
        self.storage = storage

    def _get_path(self, bible_id: str) -> str:
        """获取 Bible 文件路径

        Args:
            bible_id: Bible ID

        Returns:
            文件路径
        """
        return f"bibles/{bible_id}.json"

    def save(self, bible: Bible) -> None:
        """保存 Bible"""
        path = self._get_path(bible.id)
        data = BibleMapper.to_dict(bible)
        self.storage.write_json(path, data)

    def get_by_id(self, bible_id: str) -> Optional[Bible]:
        """根据 ID 获取 Bible"""
        path = self._get_path(bible_id)

        if not self.storage.exists(path):
            return None

        try:
            data = self.storage.read_json(path)
            return BibleMapper.from_dict(data)
        except Exception as e:
            logger.warning(f"Failed to load bible from {path}: {str(e)}")
            return None

    def get_by_novel_id(self, novel_id: NovelId) -> Optional[Bible]:
        """根据小说 ID 获取 Bible

        遍历所有 Bible 文件查找匹配的小说 ID。

        Args:
            novel_id: 小说 ID

        Returns:
            匹配的 Bible，如果不存在则返回 None
        """
        files = self.storage.list_files("bibles/*.json")

        for file_path in files:
            try:
                data = self.storage.read_json(file_path)
                if data.get("novel_id") == novel_id.value:
                    return BibleMapper.from_dict(data)
            except Exception as e:
                # 跳过损坏的文件，记录警告
                logger.warning(f"Failed to load bible from {file_path}: {str(e)}")
                continue

        return None

    def delete(self, bible_id: str) -> None:
        """删除 Bible"""
        path = self._get_path(bible_id)
        self.storage.delete(path)

    def exists(self, bible_id: str) -> bool:
        """检查 Bible 是否存在"""
        path = self._get_path(bible_id)
        return self.storage.exists(path)
