"""创建测试数据：人物和地点三元组"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.persistence.database.connection import DatabaseConnection
from infrastructure.persistence.database.sqlite_knowledge_repository import SqliteKnowledgeRepository


def create_test_data():
    """创建测试数据"""
    db = DatabaseConnection("data/aitext.db")
    repo = SqliteKnowledgeRepository(db)

    # 使用现有的小说 ID
    novel_id = "novel-1775150981848"

    print(f"为小说 {novel_id} 创建测试数据...")

    # 测试数据：人物和地点三元组
    test_data = {
        "version": 1,
        "premise_lock": "测试梗概：一个修仙世界的故事",
        "chapters": [
            {
                "number": 1,
                "chapter_id": 1,
                "summary": "主角林晨在江城觉醒，开始修炼之路"
            }
        ],
        "facts": [
            # 人物节点定义
            {
                "id": "char-linchen",
                "subject": "林晨",
                "predicate": "是",
                "object": "主角",
                "chapter_id": None,
                "note": "天赋异禀的修炼者",
                "entity_type": "character",
                "importance": "primary"
            },
            {
                "id": "char-liuyue",
                "subject": "柳月",
                "predicate": "是",
                "object": "重要配角",
                "chapter_id": None,
                "note": "林晨的师姐，冰系修炼者",
                "entity_type": "character",
                "importance": "secondary"
            },
            {
                "id": "char-zhangsan",
                "subject": "张三",
                "predicate": "是",
                "object": "次要人物",
                "chapter_id": None,
                "note": "江城守卫",
                "entity_type": "character",
                "importance": "minor"
            },

            # 人物关系
            {
                "id": "rel-linchen-liuyue",
                "subject": "林晨",
                "predicate": "师徒",
                "object": "柳月",
                "chapter_id": None,
                "note": "柳月是林晨的师姐",
                "entity_type": "character"
            },
            {
                "id": "rel-linchen-zhangsan",
                "subject": "林晨",
                "predicate": "朋友",
                "object": "张三",
                "chapter_id": None,
                "note": "青梅竹马",
                "entity_type": "character"
            },

            # 地点节点定义
            {
                "id": "loc-jiangcheng",
                "subject": "江城",
                "predicate": "是",
                "object": "核心地点",
                "chapter_id": None,
                "note": "故事主要发生地，修炼者聚集的城市",
                "entity_type": "location",
                "importance": "core",
                "location_type": "city"
            },
            {
                "id": "loc-tianxuanzong",
                "subject": "天玄宗",
                "predicate": "是",
                "object": "重要地点",
                "chapter_id": None,
                "note": "江城最大的修炼宗门",
                "entity_type": "location",
                "importance": "important",
                "location_type": "faction"
            },
            {
                "id": "loc-xuanwuge",
                "subject": "玄武阁",
                "predicate": "是",
                "object": "一般地点",
                "chapter_id": None,
                "note": "天玄宗的藏书楼",
                "entity_type": "location",
                "importance": "normal",
                "location_type": "building"
            },
            {
                "id": "loc-beiyuanyu",
                "subject": "北渊域",
                "predicate": "是",
                "object": "重要地点",
                "chapter_id": None,
                "note": "江城所在的修炼区域",
                "entity_type": "location",
                "importance": "important",
                "location_type": "region"
            },

            # 地点关系
            {
                "id": "rel-jiangcheng-beiyuanyu",
                "subject": "江城",
                "predicate": "位于",
                "object": "北渊域",
                "chapter_id": None,
                "note": "江城是北渊域的中心城市",
                "entity_type": "location"
            },
            {
                "id": "rel-tianxuanzong-jiangcheng",
                "subject": "天玄宗",
                "predicate": "坐落于",
                "object": "江城",
                "chapter_id": None,
                "note": "天玄宗位于江城北部",
                "entity_type": "location"
            },
            {
                "id": "rel-xuanwuge-tianxuanzong",
                "subject": "玄武阁",
                "predicate": "属于",
                "object": "天玄宗",
                "chapter_id": None,
                "note": "玄武阁是天玄宗的建筑",
                "entity_type": "location"
            },

            # 人物与地点的关系
            {
                "id": "rel-linchen-jiangcheng",
                "subject": "林晨",
                "predicate": "出生于",
                "object": "江城",
                "chapter_id": None,
                "note": "林晨是江城本地人"
            },
            {
                "id": "rel-liuyue-tianxuanzong",
                "subject": "柳月",
                "predicate": "修炼于",
                "object": "天玄宗",
                "chapter_id": None,
                "note": "柳月是天玄宗弟子"
            }
        ]
    }

    print(f"\n准备保存 {len(test_data['facts'])} 条三元组...")
    print(f"- 人物节点: 3 个")
    print(f"- 人物关系: 2 条")
    print(f"- 地点节点: 4 个")
    print(f"- 地点关系: 3 条")
    print(f"- 人物-地点关系: 2 条")

    # 保存数据
    repo.save_all(novel_id, test_data)

    print("\n✓ 测试数据创建成功！")
    print("\n验证步骤：")
    print("1. 访问 http://localhost:3003")
    print("2. 进入小说详情页")
    print("3. 切换到「关系图」标签")
    print("4. 点击「人物关系图」按钮，应该看到：")
    print("   - 林晨（主角，红色）")
    print("   - 柳月（重要配角，橙色）")
    print("   - 张三（次要人物，蓝色）")
    print("   - 师徒和朋友关系")
    print("5. 点击「地点关系图」按钮，应该看到：")
    print("   - 江城（核心地点，深绿色，圆形）")
    print("   - 天玄宗（重要地点，浅绿色，菱形）")
    print("   - 玄武阁（一般地点，灰色，三角形）")
    print("   - 北渊域（重要地点，浅绿色，方形）")
    print("   - 位于、坐落于、属于关系")


if __name__ == "__main__":
    create_test_data()
