"""测试增强版节拍表生成服务

验证 Phase 1.2 的完整功能：
- 地点检索
- 时间线检索
- 智能去重
- Tokens 控制
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from load_env import load_env
load_env()

from application.services.beat_sheet_service import BeatSheetService
from infrastructure.persistence.database.sqlite_beat_sheet_repository import SqliteBeatSheetRepository
from infrastructure.persistence.database.sqlite_chapter_repository import SqliteChapterRepository
from infrastructure.persistence.database.sqlite_storyline_repository import SqliteStorylineRepository
from infrastructure.persistence.database.connection import get_database
from infrastructure.ai.providers.anthropic_provider import AnthropicProvider
from infrastructure.ai.config.settings import Settings
from infrastructure.ai.chromadb_vector_store import ChromaDBVectorStore
from infrastructure.ai.local_embedding_service import LocalEmbeddingService
from domain.novel.value_objects.novel_id import NovelId
import os


async def test_enhanced_retrieval():
    """测试增强版检索功能"""

    print("=" * 80)
    print("测试增强版节拍表生成服务（Phase 1.2）")
    print("=" * 80)

    # 初始化依赖
    db = get_database()
    beat_sheet_repo = SqliteBeatSheetRepository(db)
    chapter_repo = SqliteChapterRepository(db)
    storyline_repo = SqliteStorylineRepository(db)

    # 初始化 LLM 服务
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 或 ANTHROPIC_AUTH_TOKEN 未设置")
        return

    base_url = os.getenv("ANTHROPIC_BASE_URL")
    settings = Settings(api_key=api_key, base_url=base_url)
    llm_service = AnthropicProvider(settings)

    # 初始化向量存储（使用本地模型）
    print("\n📦 初始化向量存储...")
    embedding_service = LocalEmbeddingService()
    vector_store = ChromaDBVectorStore(persist_directory="./data/chromadb")
    print(f"✅ 向量存储初始化完成 (维度: {embedding_service.get_dimension()}, 设备: {embedding_service.device})")

    # 创建服务
    service = BeatSheetService(
        beat_sheet_repo=beat_sheet_repo,
        chapter_repo=chapter_repo,
        storyline_repo=storyline_repo,
        llm_service=llm_service,
        vector_store=vector_store,
        bible_service=None
    )

    # 测试参数
    novel_id = NovelId("novel-1775380284512")
    chapter_number = 1

    # 获取章节
    chapter = chapter_repo.get_by_novel_and_number(novel_id, chapter_number)
    if not chapter:
        print(f"❌ 章节 {chapter_number} 不存在")
        return

    print(f"\n📖 测试章节: 第 {chapter_number} 章《{chapter.title}》")
    print(f"   大纲: {chapter.outline[:100]}...")

    # 测试检索功能
    print("\n" + "=" * 80)
    print("第一步：测试混合检索策略")
    print("=" * 80)

    context = await service._retrieve_relevant_context(
        chapter_id=chapter.id,
        outline=chapter.outline,
        max_tokens=3000
    )

    print(f"\n✅ 检索完成")
    print(f"\n📊 检索结果统计:")
    print(f"   - 主要人物: {len(context.get('characters', []))} 个")
    print(f"   - 活跃故事线: {len(context.get('storylines', []))} 条")
    print(f"   - 前置章节: {'有' if context.get('previous_chapter') else '无'}")
    print(f"   - 相关伏笔: {len(context.get('foreshadowings', []))} 条")
    print(f"   - 相关地点: {len(context.get('locations', []))} 个")
    print(f"   - 时间线事件: {len(context.get('timeline_events', []))} 个")

    # 显示详细信息
    if context.get('characters'):
        print(f"\n👥 主要人物:")
        for char in context['characters']:
            print(f"   - {char['name']} ({char['role']})")

    if context.get('storylines'):
        print(f"\n📖 活跃故事线:")
        for sl in context['storylines']:
            print(f"   - {sl['name']} ({sl['type']})")

    if context.get('foreshadowings'):
        print(f"\n🔮 相关伏笔:")
        for f in context['foreshadowings']:
            print(f"   - {f['description'][:50]}... (第 {f['chapter']} 章)")

    if context.get('locations'):
        print(f"\n📍 相关地点:")
        for loc in context['locations']:
            print(f"   - {loc['name']}: {loc['description'][:50]}...")

    if context.get('timeline_events'):
        print(f"\n⏰ 时间线事件:")
        for event in context['timeline_events']:
            print(f"   - 第 {event['chapter']} 章: {event['description'][:50]}...")

    # 测试生成节拍表
    print("\n" + "=" * 80)
    print("第二步：生成节拍表")
    print("=" * 80)

    try:
        beat_sheet = await service.generate_beat_sheet(
            chapter_id=chapter.id,
            outline=chapter.outline
        )

        print(f"\n✅ 节拍表生成成功")
        print(f"   章节 ID: {beat_sheet.chapter_id}")
        print(f"   场景数量: {len(beat_sheet.scenes)}")
        print(f"   总预估字数: {sum(s.estimated_words for s in beat_sheet.scenes)}")

        print(f"\n📋 场景列表:")
        for i, scene in enumerate(beat_sheet.scenes, 1):
            print(f"\n   场景 {i}: {scene.title}")
            print(f"      目标: {scene.goal}")
            print(f"      POV: {scene.pov_character}")
            print(f"      地点: {scene.location or '未指定'}")
            print(f"      基调: {scene.tone or '未指定'}")
            print(f"      预估字数: {scene.estimated_words}")

    except Exception as e:
        print(f"\n❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_enhanced_retrieval())
