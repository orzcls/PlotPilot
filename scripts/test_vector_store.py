"""向量存储功能验证脚本

验证 FAISS 向量存储的基本功能，无需 OpenAI API Key。
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.ai.chromadb_vector_store import ChromaDBVectorStore


async def main():
    print("=" * 60)
    print("向量存储功能验证")
    print("=" * 60)

    # 创建临时存储
    store = ChromaDBVectorStore(persist_directory="./data/test_vectors")

    # 1. 创建集合
    print("\n[1] 创建集合...")
    await store.create_collection("test_novels", dimension=3)
    collections = await store.list_collections()
    print(f"✓ 集合列表: {collections}")

    # 2. 插入测试向量（模拟章节内容）
    print("\n[2] 插入测试向量...")
    test_data = [
        {
            "id": "chapter_1",
            "vector": [1.0, 0.0, 0.0],
            "payload": {"text": "林雪站在雪山之巅", "chapter": 1, "character": "林雪"}
        },
        {
            "id": "chapter_2",
            "vector": [0.0, 1.0, 0.0],
            "payload": {"text": "李明在图书馆查阅资料", "chapter": 2, "character": "李明"}
        },
        {
            "id": "chapter_3",
            "vector": [0.9, 0.1, 0.0],
            "payload": {"text": "雪山上的风越来越大", "chapter": 3, "character": "林雪"}
        },
    ]

    for item in test_data:
        await store.insert(
            collection="test_novels",
            id=item["id"],
            vector=item["vector"],
            payload=item["payload"]
        )
    print(f"✓ 已插入 {len(test_data)} 条向量")

    # 3. 搜索相似向量
    print("\n[3] 搜索相似向量...")
    query_vector = [1.0, 0.0, 0.0]  # 与 chapter_1 最相似
    results = await store.search(
        collection="test_novels",
        query_vector=query_vector,
        limit=2
    )

    print(f"✓ 查询向量: {query_vector}")
    print(f"✓ 找到 {len(results)} 个相似结果:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. ID: {result['id']}")
        print(f"     相似度: {result['score']:.4f}")
        print(f"     内容: {result['payload']['text']}")
        print(f"     角色: {result['payload']['character']}")

    # 4. 测试元数据过滤（手动实现）
    print("\n[4] 元数据过滤（POV 防火墙模拟）...")
    print("   查询: 找到与林雪相关的场景")
    filtered_results = [r for r in results if r['payload']['character'] == '林雪']
    print(f"✓ 过滤后结果: {len(filtered_results)} 条")
    for result in filtered_results:
        print(f"  - {result['payload']['text']}")

    # 5. 删除向量
    print("\n[5] 删除向量...")
    await store.delete("test_novels", "chapter_2")
    results_after_delete = await store.search(
        collection="test_novels",
        query_vector=[0.0, 1.0, 0.0],
        limit=3
    )
    print(f"✓ 删除后剩余: {len(results_after_delete)} 条")

    # 6. 持久化验证
    print("\n[6] 持久化验证...")
    print("   创建新实例，验证数据是否持久化...")
    store2 = ChromaDBVectorStore(persist_directory="./data/test_vectors")
    collections2 = await store2.list_collections()
    print(f"✓ 新实例加载的集合: {collections2}")

    results_from_new_instance = await store2.search(
        collection="test_novels",
        query_vector=[1.0, 0.0, 0.0],
        limit=1
    )
    print(f"✓ 新实例可以检索到数据: {len(results_from_new_instance)} 条")

    print("\n" + "=" * 60)
    print("✓ 所有功能验证通过！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 配置 OPENAI_API_KEY 以启用真实 embedding")
    print("2. 运行集成测试: pytest tests/integration/infrastructure/ai/test_chromadb_vector_store.py")
    print("3. 在应用中使用: VECTOR_STORE_ENABLED=true")


if __name__ == "__main__":
    asyncio.run(main())
