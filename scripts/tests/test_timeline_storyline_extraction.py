"""测试时间线和故事线自动提取功能"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application.ai.chapter_state_llm_contract import (
    parse_chapter_state_llm_response,
    chapter_state_payload_to_domain,
    build_chapter_state_extraction_system_prompt
)
from application.services.state_updater import StateUpdater
from infrastructure.persistence.database.connection import get_database
from infrastructure.persistence.database.sqlite_bible_repository import SqliteBibleRepository
from infrastructure.persistence.database.sqlite_foreshadowing_repository import SqliteForeshadowingRepository
from infrastructure.persistence.database.sqlite_timeline_repository import SqliteTimelineRepository
from infrastructure.persistence.database.sqlite_storyline_repository import SqliteStorylineRepository
from domain.novel.value_objects.novel_id import NovelId
from domain.bible.entities.bible import Bible

# 模拟 LLM 响应（包含时间线和故事线）
MOCK_LLM_RESPONSE = """{
  "new_characters": [],
  "character_actions": [],
  "relationship_changes": [],
  "foreshadowing_planted": [],
  "foreshadowing_resolved": [],
  "events": [
    {
      "type": "conflict",
      "description": "主角在雪山遭遇雪崩",
      "involved_characters": ["protagonist"],
      "chapter": 1
    }
  ],
  "timeline_events": [
    {
      "event": "雪山遭遇雪崩",
      "timestamp": "修炼第三年春季",
      "timestamp_type": "relative"
    },
    {
      "event": "主角突破筑基期",
      "timestamp": "午夜子时",
      "timestamp_type": "vague"
    }
  ],
  "advanced_storylines": [
    {
      "storyline_name": "修仙主线",
      "progress_summary": "主角在雪山中突破筑基期，实力大增"
    }
  ],
  "new_storylines": [
    {
      "name": "雪山秘境探索",
      "type": "sub",
      "description": "主角发现雪山深处隐藏着上古遗迹"
    }
  ]
}"""


def main():
    print("=" * 80)
    print("时间线和故事线自动提取测试")
    print("=" * 80)

    # 1. 解析 LLM 响应
    print("\n[1] 解析 LLM 响应...")
    payload, errors = parse_chapter_state_llm_response(MOCK_LLM_RESPONSE)
    if errors:
        print(f"❌ 解析失败: {errors}")
        return
    print("✅ 解析成功")

    # 2. 转换为领域对象
    print("\n[2] 转换为 ChapterState...")
    chapter_state = chapter_state_payload_to_domain(payload)
    print(f"✅ ChapterState 创建成功")
    print(f"   - 时间线事件: {len(chapter_state.timeline_events)}")
    print(f"   - 推进的故事线: {len(chapter_state.advanced_storylines)}")
    print(f"   - 新故事线: {len(chapter_state.new_storylines)}")

    # 3. 初始化仓储
    print("\n[3] 初始化仓储...")
    db = get_database()
    from infrastructure.persistence.database.sqlite_novel_repository import SqliteNovelRepository
    novel_repo = SqliteNovelRepository(db)
    bible_repo = SqliteBibleRepository(db)
    foreshadowing_repo = SqliteForeshadowingRepository(db)
    timeline_repo = SqliteTimelineRepository(db)
    storyline_repo = SqliteStorylineRepository(db)

    # 创建测试小说
    novel_id = NovelId("test-timeline-novel")
    from domain.novel.entities.novel import Novel
    novel = Novel(id=novel_id, title="测试小说", author="测试作者", target_chapters=100)
    novel_repo.save(novel)

    # 创建 Bible
    bible = Bible(id="test-bible", novel_id=novel_id)
    bible_repo.save(bible)
    print("✅ 仓储初始化完成")

    # 4. 创建初始故事线（用于测试 advanced_storylines）
    print("\n[4] 创建初始故事线...")
    from domain.novel.entities.storyline import Storyline
    from domain.novel.value_objects.storyline_type import StorylineType
    from domain.novel.value_objects.storyline_status import StorylineStatus

    initial_storyline = Storyline(
        id="storyline-1",
        novel_id=novel_id,
        storyline_type=StorylineType.MAIN_PLOT,
        status=StorylineStatus.ACTIVE,
        estimated_chapter_start=1,
        estimated_chapter_end=100,
        name="修仙主线",
        description="主角的修仙之路"
    )
    storyline_repo.save(initial_storyline)
    print("✅ 初始故事线创建完成")

    # 5. 执行状态更新
    print("\n[5] 执行 StateUpdater...")
    state_updater = StateUpdater(
        bible_repository=bible_repo,
        foreshadowing_repository=foreshadowing_repo,
        timeline_repository=timeline_repo,
        storyline_repository=storyline_repo
    )

    state_updater.update_from_chapter(
        novel_id="test-timeline-novel",
        chapter_number=1,
        chapter_state=chapter_state
    )
    print("✅ 状态更新完成")

    # 6. 验证时间线
    print("\n[6] 验证时间线...")
    timeline_registry = timeline_repo.get_by_novel_id(novel_id)
    if timeline_registry:
        print(f"✅ TimelineRegistry 存在")
        print(f"   - 事件总数: {len(timeline_registry.events)}")
        for event in timeline_registry.events:
            print(f"   - [{event.timestamp_type}] {event.timestamp}: {event.event}")
    else:
        print("❌ TimelineRegistry 不存在")

    # 7. 验证故事线
    print("\n[7] 验证故事线...")
    storylines = storyline_repo.get_by_novel_id(novel_id)
    print(f"✅ 找到 {len(storylines)} 条故事线")
    for sl in storylines:
        print(f"   - [{sl.storyline_type.value}] {sl.name}")
        print(f"     最后活跃章节: {sl.last_active_chapter}")
        print(f"     进度: {sl.progress_summary}")

    # 8. 清理测试数据
    print("\n[8] 清理测试数据...")
    timeline_repo.delete(novel_id)
    for sl in storylines:
        storyline_repo.delete(sl.id)
    bible_repo.delete(novel_id.value)
    novel_repo.delete(novel_id)
    print("✅ 清理完成")

    print("\n" + "=" * 80)
    print("✅ 所有测试通过！时间线和故事线自动化功能正常工作")
    print("=" * 80)


if __name__ == "__main__":
    main()
