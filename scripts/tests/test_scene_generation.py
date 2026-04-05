"""测试场景生成服务"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from application.services.scene_generation_service import SceneGenerationService
from application.services.scene_director_service import SceneDirectorService
from application.services.beat_sheet_service import BeatSheetService
from infrastructure.persistence.database.sqlite_beat_sheet_repository import SqliteBeatSheetRepository
from infrastructure.persistence.database.sqlite_chapter_repository import SqliteChapterRepository
from infrastructure.persistence.database.sqlite_storyline_repository import SqliteStorylineRepository
from infrastructure.persistence.database.connection import get_database
from infrastructure.ai.providers.anthropic_provider import AnthropicProvider
from infrastructure.ai.config.settings import Settings
from infrastructure.ai.chromadb_vector_store import ChromaDBVectorStore
import os


async def test_scene_generation():
    """测试场景生成"""

    # 初始化依赖
    db = get_database()
    beat_sheet_repo = SqliteBeatSheetRepository(db)

    # 初始化 LLM 服务
    api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY 或 ANTHROPIC_AUTH_TOKEN 未设置")
        return

    base_url = os.getenv("ANTHROPIC_BASE_URL")
    settings = Settings(api_key=api_key, base_url=base_url)
    llm_service = AnthropicProvider(settings)

    # 初始化场记服务
    scene_director = SceneDirectorService(llm_service)

    # 初始化向量存储
    vector_store = ChromaDBVectorStore(persist_directory="./data/chromadb")

    # 创建场景生成服务
    scene_gen_service = SceneGenerationService(
        llm_service=llm_service,
        scene_director=scene_director,
        vector_store=vector_store,
        embedding_service=None
    )

    # 测试章节 ID（使用之前生成的节拍表）
    test_chapter_id = "test-chapter-001"
    chapter_number = 1

    print("=" * 80)
    print("🎬 测试场景生成服务")
    print("=" * 80)

    # 1. 获取节拍表
    print(f"\n📋 获取节拍表: {test_chapter_id}")
    beat_sheet = await beat_sheet_repo.get_by_chapter_id(test_chapter_id)
    if not beat_sheet:
        print("❌ 节拍表不存在，请先运行 test_beat_sheet_generation.py")
        return

    print(f"✅ 节拍表包含 {len(beat_sheet.scenes)} 个场景\n")

    # 2. 生成第一个场景
    scene_index = 0
    target_scene = beat_sheet.scenes[scene_index]

    print("=" * 80)
    print(f"📝 生成场景 {scene_index + 1}: {target_scene.title}")
    print("=" * 80)
    print(f"目标: {target_scene.goal}")
    print(f"POV: {target_scene.pov_character}")
    print(f"地点: {target_scene.location or '未指定'}")
    print(f"基调: {target_scene.tone or '未指定'}")
    print(f"预估字数: {target_scene.estimated_words}\n")

    print("正在生成场景正文...\n")

    try:
        # 生成场景正文
        content = await scene_gen_service.generate_scene(
            scene=target_scene,
            chapter_number=chapter_number,
            previous_scenes=[],  # 第一个场景，无前置场景
            bible_context=None
        )

        print("✅ 场景生成成功！\n")
        print("=" * 80)
        print("📖 生成的正文")
        print("=" * 80)
        print(content)
        print("\n" + "=" * 80)
        print(f"字数统计: {len(content)} 字")
        print("=" * 80)

        # 3. 生成第二个场景（带前置场景上下文）
        if len(beat_sheet.scenes) > 1:
            print("\n\n" + "=" * 80)
            print("📝 生成场景 2（带前置场景上下文）")
            print("=" * 80)

            scene_index = 1
            target_scene = beat_sheet.scenes[scene_index]

            print(f"场景标题: {target_scene.title}")
            print(f"目标: {target_scene.goal}")
            print(f"POV: {target_scene.pov_character}\n")

            print("正在生成场景正文...\n")

            content2 = await scene_gen_service.generate_scene(
                scene=target_scene,
                chapter_number=chapter_number,
                previous_scenes=[content],  # 传入第一个场景的正文
                bible_context=None
            )

            print("✅ 场景生成成功！\n")
            print("=" * 80)
            print("📖 生成的正文")
            print("=" * 80)
            print(content2)
            print("\n" + "=" * 80)
            print(f"字数统计: {len(content2)} 字")
            print("=" * 80)

        print("\n\n" + "=" * 80)
        print("✅ 测试完成！")
        print("=" * 80)

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_scene_generation())
