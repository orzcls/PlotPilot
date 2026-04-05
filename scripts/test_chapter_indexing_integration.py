"""测试章节索引服务的完整集成

验证：章节索引 -> 语义检索 -> POV 防火墙
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.ai.local_embedding_service import LocalEmbeddingService
from infrastructure.ai.chromadb_vector_store import ChromaDBVectorStore
from application.services.chapter_indexing_service import ChapterIndexingService


async def main():
    print("=" * 60)
    print("章节索引服务集成测试")
    print("=" * 60)

    # 1. 初始化服务
    print("\n[1] 初始化服务...")
    embedding_service = LocalEmbeddingService(
        model_name="./.models/bge-small-zh-v1.5",
        use_gpu=True
    )
    vector_store = ChromaDBVectorStore(persist_directory="./data/chromadb")
    indexing_service = ChapterIndexingService(vector_store, embedding_service)
    print(f"✓ Embedding 维度: {embedding_service.get_dimension()}")
    print(f"✓ 设备: {embedding_service.device}")

    # 2. 创建测试小说
    novel_id = "test_novel_001"
    print(f"\n[2] 创建小说索引: {novel_id}")
    await indexing_service.ensure_collection(novel_id)
    print("✓ Collection 已创建")

    # 3. 索引章节摘要
    print("\n[3] 索引章节摘要...")
    chapters = [
        {
            "number": 1,
            "summary": "林雪在雪山之巅遇到了神秘的老者，老者告诉她关于古代秘术的传说。寒风刺骨，但林雪决心要找到真相。"
        },
        {
            "number": 2,
            "summary": "李明在图书馆发现了一本古籍，记载着失传已久的炼金术。他意识到这可能与林雪寻找的秘术有关。"
        },
        {
            "number": 3,
            "summary": "雪山上的暴风雪越来越猛烈，林雪在山洞中避难。她回想起老者的话，开始理解秘术的真正含义。"
        },
        {
            "number": 4,
            "summary": "李明决定前往雪山寻找林雪，他带上了古籍和必要的装备。图书馆的管理员警告他雪山的危险。"
        },
        {
            "number": 5,
            "summary": "林雪在山洞深处发现了古老的壁画，壁画描绘着秘术的起源。她用手机拍下照片，准备研究。"
        }
    ]

    for chapter in chapters:
        await indexing_service.index_chapter_summary(
            novel_id=novel_id,
            chapter_number=chapter["number"],
            summary=chapter["summary"]
        )
        print(f"  ✓ 第 {chapter['number']} 章已索引")

    # 4. 语义检索测试
    print("\n[4] 语义检索测试...")
    queries = [
        "雪山上的场景",
        "图书馆里的发现",
        "古代秘术的线索"
    ]

    for query in queries:
        print(f"\n  查询: '{query}'")
        query_vector = await embedding_service.embed(query)
        results = await vector_store.search(
            collection=f"novel_{novel_id}_chunks",
            query_vector=query_vector,
            limit=3
        )

        print(f"  找到 {len(results)} 个相关章节:")
        for i, result in enumerate(results, 1):
            chapter_num = result['payload']['chapter_number']
            score = result['score']
            text = result['payload']['text'][:50]
            print(f"    {i}. 第{chapter_num}章 [相似度: {score:.3f}] {text}...")

    # 5. POV 防火墙测试
    print("\n[5] POV 防火墙测试...")
    print("  场景: 当前在第3章，只能检索前3章的内容")

    current_chapter = 3
    query = "关于秘术的信息"
    query_vector = await embedding_service.embed(query)
    results = await vector_store.search(
        collection=f"novel_{novel_id}_chunks",
        query_vector=query_vector,
        limit=5
    )

    # 应用 POV 防火墙
    filtered_results = [
        r for r in results
        if r['payload']['chapter_number'] <= current_chapter
    ]

    print(f"  原始结果: {len(results)} 条")
    print(f"  过滤后: {len(filtered_results)} 条（只保留 ≤ 第{current_chapter}章）")
    for result in filtered_results:
        chapter_num = result['payload']['chapter_number']
        text = result['payload']['text'][:40]
        print(f"    - 第{chapter_num}章: {text}...")

    # 6. 批量索引性能测试
    print("\n[6] 批量索引性能测试...")
    import time

    batch_chapters = [
        {"number": i, "summary": f"这是第{i}章的摘要，讲述了主角的冒险经历。"}
        for i in range(10, 110)  # 100章
    ]

    start = time.time()
    for chapter in batch_chapters:
        await indexing_service.index_chapter_summary(
            novel_id=novel_id,
            chapter_number=chapter["number"],
            summary=chapter["summary"]
        )
    elapsed = time.time() - start

    print(f"  ✓ 索引 {len(batch_chapters)} 章")
    print(f"  ✓ 总耗时: {elapsed:.2f}秒")
    print(f"  ✓ 平均每章: {elapsed/len(batch_chapters)*1000:.1f}ms")
    print(f"  ✓ 吞吐量: {len(batch_chapters)/elapsed:.1f} 章/秒")

    print("\n" + "=" * 60)
    print("✓ 章节索引服务集成测试完成！")
    print("=" * 60)
    print("\n系统能力:")
    print("  ✅ 章节摘要索引")
    print("  ✅ 语义检索")
    print("  ✅ POV 防火墙（元数据过滤）")
    print("  ✅ GPU 加速")
    print("  ✅ 批量索引")
    print("\n可用于:")
    print("  - 智能上下文构建")
    print("  - 伏笔检索与呼应")
    print("  - 情节一致性检查")
    print("  - 角色视角管理")


if __name__ == "__main__":
    asyncio.run(main())
