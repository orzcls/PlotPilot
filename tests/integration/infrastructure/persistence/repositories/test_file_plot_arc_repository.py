"""FilePlotArcRepository 集成测试"""
import pytest
import tempfile
import shutil
from pathlib import Path
from domain.novel.entities.plot_arc import PlotArc
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.plot_point import PlotPoint, PlotPointType
from domain.novel.value_objects.tension_level import TensionLevel
from infrastructure.persistence.storage.file_storage import FileStorage
from infrastructure.persistence.repositories.file_plot_arc_repository import FilePlotArcRepository


class TestFilePlotArcRepository:
    """FilePlotArcRepository 集成测试"""

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
        """创建 FilePlotArcRepository 实例"""
        return FilePlotArcRepository(storage)

    def test_save_and_get(self, repository):
        """测试保存和获取剧情弧"""
        novel_id = NovelId("test-novel")
        plot_arc = PlotArc(
            id="arc-1",
            novel_id=novel_id
        )

        plot_point = PlotPoint(
            chapter_number=1,
            point_type=PlotPointType.OPENING,
            description="故事开端",
            tension=TensionLevel.LOW
        )
        plot_arc.add_plot_point(plot_point)

        repository.save(plot_arc)
        retrieved = repository.get_by_novel_id(novel_id)

        assert retrieved is not None
        assert retrieved.id == "arc-1"
        assert retrieved.novel_id.value == "test-novel"
        assert len(retrieved.key_points) == 1
        assert retrieved.key_points[0].description == "故事开端"

    def test_get_nonexistent(self, repository):
        """测试获取不存在的剧情弧"""
        result = repository.get_by_novel_id(NovelId("nonexistent"))
        assert result is None

    def test_delete(self, repository):
        """测试删除剧情弧"""
        novel_id = NovelId("test-novel")
        plot_arc = PlotArc(
            id="arc-1",
            novel_id=novel_id
        )

        repository.save(plot_arc)
        assert repository.get_by_novel_id(novel_id) is not None

        repository.delete(novel_id)
        assert repository.get_by_novel_id(novel_id) is None

    def test_save_with_multiple_plot_points(self, repository):
        """测试保存包含多个剧情点的剧情弧"""
        novel_id = NovelId("test-novel")
        plot_arc = PlotArc(
            id="arc-1",
            novel_id=novel_id
        )

        plot_arc.add_plot_point(PlotPoint(
            chapter_number=1,
            point_type=PlotPointType.OPENING,
            description="开端",
            tension=TensionLevel.LOW
        ))
        plot_arc.add_plot_point(PlotPoint(
            chapter_number=5,
            point_type=PlotPointType.CLIMAX,
            description="高潮",
            tension=TensionLevel.PEAK
        ))

        repository.save(plot_arc)
        retrieved = repository.get_by_novel_id(novel_id)

        assert len(retrieved.key_points) == 2
        assert retrieved.key_points[0].chapter_number == 1
        assert retrieved.key_points[1].chapter_number == 5

    def test_overwrite_existing(self, repository):
        """测试覆盖已存在的剧情弧"""
        novel_id = NovelId("test-novel")

        # 保存第一个版本
        plot_arc1 = PlotArc(id="arc-1", novel_id=novel_id)
        plot_arc1.add_plot_point(PlotPoint(
            chapter_number=1,
            point_type=PlotPointType.OPENING,
            description="第一版",
            tension=TensionLevel.LOW
        ))
        repository.save(plot_arc1)

        # 保存第二个版本（覆盖）
        plot_arc2 = PlotArc(id="arc-2", novel_id=novel_id)
        plot_arc2.add_plot_point(PlotPoint(
            chapter_number=2,
            point_type=PlotPointType.RISING_ACTION,
            description="第二版",
            tension=TensionLevel.MEDIUM
        ))
        repository.save(plot_arc2)

        # 应该只有第二版
        retrieved = repository.get_by_novel_id(novel_id)
        assert retrieved.id == "arc-2"
        assert len(retrieved.key_points) == 1
        assert retrieved.key_points[0].description == "第二版"
