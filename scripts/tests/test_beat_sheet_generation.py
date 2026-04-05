"""测试节拍表生成服务"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from application.services.beat_sheet_service import BeatSheetService
from infrastructure.persistence.database.sqlite_beat_sheet_repository import SqliteBeatSheetRepository
from infrastructure.persistence.database.sqlite_chapter_repository import SqliteChapterRepository
from infrastructure.persistence.database.sqlite_storyline_repository import SqliteStorylineRepository
from infrastructure.persistence.database.connection import get_database
from infrastructure.ai.providers.anthropic_provider import AnthropicProvider
from infrastructure.ai.config.settings import Settings
from infrastructure.ai.chromadb_vector_store import ChromaDBVectorStore
import os


async def test_beat_sheet_generation():
    """测试节拍表生成"""

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

    # 初始化向量存储
    vector_store = ChromaDBVectorStore(persist_directory="./data/chromadb")

    # 创建服务
    service = BeatSheetService(
        beat_sheet_repo=beat_sheet_repo,
        chapter_repo=chapter_repo,
        storyline_repo=storyline_repo,
        llm_service=llm_service,
        vector_store=vector_store,
        bible_service=None
    )

    # 测试章节大纲
    test_chapter_id = "test-chapter-001"
    test_outline = """
    第一章：初遇

    主角李明是一名普通的大学生，某天在图书馆偶然发现了一本古老的笔记本。
    笔记本中记载着一个神秘的传说，关于一座隐藏在深山中的古墓。
    李明对此产生了浓厚的兴趣，决定深入调查。
    在调查过程中，他结识了考古系的学姐王芳，两人决定一起探索这个秘密。
    """

    print("=" * 80)
    print("🎬 测试节拍表生成服务")
    print("=" * 80)
    print(f"\n章节 ID: {test_chapter_id}")
    print(f"章节大纲:\n{test_outline}")
    print("\n正在生成节拍表...\n")

    try:
        # 生成节拍表
        beat_sheet = await service.generate_beat_sheet(
            chapter_id=test_chapter_id,
            outline=test_outline
        )

        print("✅ 节拍表生成成功！\n")
        print(f"节拍表 ID: {beat_sheet.id}")
        print(f"章节 ID: {beat_sheet.chapter_id}")
        print(f"场景数量: {beat_sheet.get_scene_count()}")
        print(f"预估总字数: {beat_sheet.get_total_estimated_words()}\n")

        print("=" * 80)
        print("📋 场景列表")
        print("=" * 80)

        for i, scene in enumerate(beat_sheet.scenes, 1):
            print(f"\n【场景 {i}】{scene.title}")
            print(f"  目标: {scene.goal}")
            print(f"  POV: {scene.pov_character}")
            print(f"  地点: {scene.location or '未指定'}")
            print(f"  基调: {scene.tone or '未指定'}")
            print(f"  预估字数: {scene.estimated_words}")

        print("\n" + "=" * 80)
        print("✅ 测试完成！")
        print("=" * 80)

        # 测试获取节拍表
        print("\n测试获取节拍表...")
        retrieved = await service.get_beat_sheet(test_chapter_id)
        if retrieved:
            print(f"✅ 成功获取节拍表，包含 {retrieved.get_scene_count()} 个场景")
        else:
            print("❌ 获取节拍表失败")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_beat_sheet_generation())
