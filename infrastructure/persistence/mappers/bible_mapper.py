"""Bible 数据映射器"""
from typing import Dict, Any
from domain.bible.entities.bible import Bible
from domain.bible.entities.character import Character
from domain.bible.entities.world_setting import WorldSetting
from domain.bible.value_objects.character_id import CharacterId
from domain.novel.value_objects.novel_id import NovelId


class BibleMapper:
    """Bible 实体与字典数据之间的映射器

    负责将 Bible 领域对象转换为可持久化的字典格式，
    以及从字典数据重建 Bible 对象。
    """

    @staticmethod
    def to_dict(bible: Bible) -> Dict[str, Any]:
        """将 Bible 实体转换为字典

        Args:
            bible: Bible 实体

        Returns:
            字典表示
        """
        return {
            "id": bible.id,
            "novel_id": bible.novel_id.value,
            "characters": [
                {
                    "id": char.character_id.value,
                    "name": char.name,
                    "description": char.description,
                    "relationships": char.relationships
                }
                for char in bible.characters
            ],
            "world_settings": [
                {
                    "id": setting.id,
                    "name": setting.name,
                    "description": setting.description,
                    "setting_type": setting.setting_type
                }
                for setting in bible.world_settings
            ]
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Bible:
        """从字典创建 Bible 实体

        Args:
            data: 字典数据

        Returns:
            Bible 实体

        Raises:
            ValueError: 如果数据格式不正确或缺少必需字段
        """
        # 验证必需字段
        required_fields = ["id", "novel_id"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            # 创建 Bible 实体
            bible = Bible(
                id=data["id"],
                novel_id=NovelId(data["novel_id"])
            )

            # 添加人物
            for char_data in data.get("characters", []):
                # 验证人物必需字段
                char_required = ["id", "name", "description"]
                char_missing = [field for field in char_required if field not in char_data]
                if char_missing:
                    raise ValueError(f"Character missing required fields: {', '.join(char_missing)}")

                character = Character(
                    id=CharacterId(char_data["id"]),
                    name=char_data["name"],
                    description=char_data["description"],
                    relationships=char_data.get("relationships", [])
                )
                bible.add_character(character)

            # 添加世界设定
            for setting_data in data.get("world_settings", []):
                # 验证世界设定必需字段
                setting_required = ["id", "name", "description", "setting_type"]
                setting_missing = [field for field in setting_required if field not in setting_data]
                if setting_missing:
                    raise ValueError(f"World setting missing required fields: {', '.join(setting_missing)}")

                setting = WorldSetting(
                    id=setting_data["id"],
                    name=setting_data["name"],
                    description=setting_data["description"],
                    setting_type=setting_data["setting_type"]
                )
                bible.add_world_setting(setting)

            return bible
        except (ValueError, KeyError) as e:
            raise ValueError(f"Invalid bible data format: {str(e)}") from e
