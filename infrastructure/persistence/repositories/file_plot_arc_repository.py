"""基于文件的 PlotArc 仓储实现"""
import logging
from typing import Optional
from domain.novel.entities.plot_arc import PlotArc
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.repositories.plot_arc_repository import PlotArcRepository
from infrastructure.persistence.storage.backend import StorageBackend
from infrastructure.persistence.mappers.plot_arc_mapper import PlotArcMapper

logger = logging.getLogger(__name__)


class FilePlotArcRepository(PlotArcRepository):
    """基于文件系统的 PlotArc 仓储实现

    使用 JSON 文件存储剧情弧数据。
    """

    def __init__(self, storage: StorageBackend):
        """初始化仓储

        Args:
            storage: 存储后端
        """
        self.storage = storage

    def _get_path(self, novel_id: NovelId) -> str:
        """获取剧情弧文件路径

        Args:
            novel_id: 小说 ID

        Returns:
            文件路径
        """
        return f"plot_arcs/{novel_id.value}.json"

    def save(self, plot_arc: PlotArc) -> None:
        """保存剧情弧"""
        path = self._get_path(plot_arc.novel_id)
        data = PlotArcMapper.to_dict(plot_arc)
        self.storage.write_json(path, data)

    def get_by_novel_id(self, novel_id: NovelId) -> Optional[PlotArc]:
        """根据小说 ID 获取剧情弧"""
        path = self._get_path(novel_id)

        if not self.storage.exists(path):
            return None

        data = self.storage.read_json(path)
        return PlotArcMapper.from_dict(data)

    def delete(self, novel_id: NovelId) -> None:
        """删除剧情弧"""
        path = self._get_path(novel_id)
        self.storage.delete(path)
