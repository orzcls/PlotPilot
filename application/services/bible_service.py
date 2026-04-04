"""Bible 应用服务"""
from typing import TYPE_CHECKING, Optional

from domain.bible.entities.bible import Bible
from domain.bible.entities.character import Character
from domain.bible.entities.world_setting import WorldSetting
from domain.bible.entities.location import Location
from domain.bible.entities.timeline_note import TimelineNote
from domain.bible.entities.style_note import StyleNote
from domain.bible.value_objects.character_id import CharacterId
from domain.novel.value_objects.novel_id import NovelId
from domain.bible.repositories.bible_repository import BibleRepository
from domain.shared.exceptions import EntityNotFoundError
from application.dtos.bible_dto import BibleDTO

if TYPE_CHECKING:
    from application.services.bible_location_triple_sync import BibleLocationTripleSyncService


class BibleService:
    """Bible 应用服务"""

    def __init__(
        self,
        bible_repository: BibleRepository,
        location_triple_sync: Optional["BibleLocationTripleSyncService"] = None,
    ):
        """初始化服务

        Args:
            bible_repository: Bible 仓储
            location_triple_sync: 可选；保存 Bible 后将 locations 同步到 triples
        """
        self.bible_repository = bible_repository
        self._location_triple_sync = location_triple_sync

    def _validate_locations_forest(self, locations: list) -> None:
        from domain.bible.bible_location_tree import validate_location_forest

        forest = [{"id": ld.id, "parent_id": getattr(ld, "parent_id", None)} for ld in locations]
        validate_location_forest(forest)

    def _sync_location_triples(self, novel_id: str, bible: Bible) -> None:
        if self._location_triple_sync is None:
            return
        locs = [
            {
                "id": loc.id.strip(),
                "name": loc.name.strip(),
                "parent_id": loc.parent_id,
                "type": (loc.location_type or "").strip(),
            }
            for loc in bible.locations
        ]
        self._location_triple_sync.sync_from_locations(novel_id, locs)

    def create_bible(self, bible_id: str, novel_id: str) -> BibleDTO:
        """创建 Bible

        Args:
            bible_id: Bible ID
            novel_id: 小说 ID

        Returns:
            BibleDTO
        """
        bible = Bible(id=bible_id, novel_id=NovelId(novel_id))
        self.bible_repository.save(bible)
        return BibleDTO.from_domain(bible)

    def add_character(
        self,
        novel_id: str,
        character_id: str,
        name: str,
        description: str,
        relationships: list = None
    ) -> BibleDTO:
        """添加人物

        Args:
            novel_id: 小说 ID
            character_id: 人物 ID
            name: 人物名称
            description: 人物描述
            relationships: 人物关系列表

        Returns:
            更新后的 BibleDTO

        Raises:
            EntityNotFoundError: 如果 Bible 不存在
        """
        bible = self.bible_repository.get_by_novel_id(NovelId(novel_id))
        if bible is None:
            raise EntityNotFoundError("Bible", f"for novel {novel_id}")

        character = Character(
            id=CharacterId(character_id),
            name=name,
            description=description,
            relationships=relationships or []
        )
        bible.add_character(character)
        self.bible_repository.save(bible)

        return BibleDTO.from_domain(bible)

    def add_world_setting(
        self,
        novel_id: str,
        setting_id: str,
        name: str,
        description: str,
        setting_type: str
    ) -> BibleDTO:
        """添加世界设定

        Args:
            novel_id: 小说 ID
            setting_id: 设定 ID
            name: 设定名称
            description: 设定描述
            setting_type: 设定类型

        Returns:
            更新后的 BibleDTO

        Raises:
            EntityNotFoundError: 如果 Bible 不存在
        """
        bible = self.bible_repository.get_by_novel_id(NovelId(novel_id))
        if bible is None:
            raise EntityNotFoundError("Bible", f"for novel {novel_id}")

        setting = WorldSetting(
            id=setting_id,
            name=name,
            description=description,
            setting_type=setting_type
        )
        bible.add_world_setting(setting)
        self.bible_repository.save(bible)

        return BibleDTO.from_domain(bible)

    def add_location(
        self,
        novel_id: str,
        location_id: str,
        name: str,
        description: str,
        location_type: str,
        connections: list = None,
        parent_id: Optional[str] = None,
    ) -> BibleDTO:
        """添加地点

        Args:
            novel_id: 小说 ID
            location_id: 地点 ID
            name: 地点名称
            description: 地点描述
            location_type: 地点类型
            connections: 地点关系列表

        Returns:
            更新后的 BibleDTO

        Raises:
            EntityNotFoundError: 如果 Bible 不存在
        """
        bible = self.bible_repository.get_by_novel_id(NovelId(novel_id))
        if bible is None:
            raise EntityNotFoundError("Bible", f"for novel {novel_id}")

        pid = parent_id.strip() if isinstance(parent_id, str) and parent_id.strip() else None
        location = Location(
            id=location_id,
            name=name,
            description=description,
            location_type=location_type,
            connections=connections or [],
            parent_id=pid,
        )
        bible.add_location(location)
        from domain.bible.bible_location_tree import validate_location_forest

        validate_location_forest(
            [{"id": loc.id, "parent_id": loc.parent_id} for loc in bible.locations]
        )
        self.bible_repository.save(bible)
        self._sync_location_triples(novel_id, bible)

        return BibleDTO.from_domain(bible)

    def add_timeline_note(
        self,
        novel_id: str,
        note_id: str,
        event: str,
        time_point: str,
        description: str
    ) -> BibleDTO:
        """添加时间线笔记

        Args:
            novel_id: 小说 ID
            note_id: 笔记 ID
            event: 事件
            time_point: 时间点
            description: 描述

        Returns:
            更新后的 BibleDTO

        Raises:
            EntityNotFoundError: 如果 Bible 不存在
        """
        bible = self.bible_repository.get_by_novel_id(NovelId(novel_id))
        if bible is None:
            raise EntityNotFoundError("Bible", f"for novel {novel_id}")

        note = TimelineNote(
            id=note_id,
            event=event,
            time_point=time_point,
            description=description
        )
        bible.add_timeline_note(note)
        self.bible_repository.save(bible)

        return BibleDTO.from_domain(bible)

    def add_style_note(
        self,
        novel_id: str,
        note_id: str,
        category: str,
        content: str
    ) -> BibleDTO:
        """添加风格笔记

        Args:
            novel_id: 小说 ID
            note_id: 笔记 ID
            category: 类别
            content: 内容

        Returns:
            更新后的 BibleDTO

        Raises:
            EntityNotFoundError: 如果 Bible 不存在
        """
        bible = self.bible_repository.get_by_novel_id(NovelId(novel_id))
        if bible is None:
            raise EntityNotFoundError("Bible", f"for novel {novel_id}")

        note = StyleNote(
            id=note_id,
            category=category,
            content=content
        )
        bible.add_style_note(note)
        self.bible_repository.save(bible)

        return BibleDTO.from_domain(bible)

    def get_bible_by_novel(self, novel_id: str) -> Optional[BibleDTO]:
        """根据小说 ID 获取 Bible

        Args:
            novel_id: 小说 ID

        Returns:
            BibleDTO 或 None
        """
        bible = self.bible_repository.get_by_novel_id(NovelId(novel_id))
        if bible is None:
            return None
        return BibleDTO.from_domain(bible)

    def update_bible(
        self,
        novel_id: str,
        characters: list,
        world_settings: list,
        locations: list,
        timeline_notes: list,
        style_notes: list
    ) -> BibleDTO:
        """批量更新 Bible 的所有数据

        Args:
            novel_id: 小说 ID
            characters: 人物列表
            world_settings: 世界设定列表
            locations: 地点列表
            timeline_notes: 时间线笔记列表
            style_notes: 风格笔记列表

        Returns:
            更新后的 BibleDTO

        Raises:
            EntityNotFoundError: 如果 Bible 不存在
        """
        bible = self.bible_repository.get_by_novel_id(NovelId(novel_id))
        if bible is None:
            raise EntityNotFoundError("Bible", f"for novel {novel_id}")

        self._validate_locations_forest(locations)

        # 清空现有数据
        bible._characters = []
        bible._world_settings = []
        bible._locations = []
        bible._timeline_notes = []
        bible._style_notes = []

        # 添加新的人物
        for char_data in characters:
            character = Character(
                id=CharacterId(char_data.id),
                name=char_data.name,
                description=char_data.description,
                relationships=char_data.relationships
            )
            bible._characters.append(character)

        # 添加新的世界设定
        for setting_data in world_settings:
            setting = WorldSetting(
                id=setting_data.id,
                name=setting_data.name,
                description=setting_data.description,
                setting_type=setting_data.setting_type
            )
            bible._world_settings.append(setting)

        # 添加新的地点
        for loc_data in locations:
            raw_pid = getattr(loc_data, "parent_id", None)
            pid = raw_pid.strip() if isinstance(raw_pid, str) and raw_pid.strip() else None
            location = Location(
                id=loc_data.id,
                name=loc_data.name,
                description=loc_data.description,
                location_type=loc_data.location_type,
                parent_id=pid,
            )
            bible._locations.append(location)

        # 添加新的时间线笔记
        for note_data in timeline_notes:
            note = TimelineNote(
                id=note_data.id,
                event=note_data.event,
                time_point=note_data.time_point,
                description=note_data.description
            )
            bible._timeline_notes.append(note)

        # 添加新的风格笔记
        for note_data in style_notes:
            note = StyleNote(
                id=note_data.id,
                category=note_data.category,
                content=note_data.content
            )
            bible._style_notes.append(note)

        self.bible_repository.save(bible)
        self._sync_location_triples(novel_id, bible)
        return BibleDTO.from_domain(bible)
