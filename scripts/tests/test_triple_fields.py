"""
测试脚本：添加带有 entity_type 和 importance 的三元组
"""
import requests
import json

BASE_URL = "http://localhost:8007/api/v1"
NOVEL_ID = "novel-1775150981848"

# 测试数据：人物三元组
character_triples = [
    {
        "id": "char-001",
        "subject": "林晨",
        "predicate": "是主角",
        "object": "风水师",
        "entity_type": "character",
        "importance": "primary",
        "note": "主角，意外获得风水天赋"
    },
    {
        "id": "char-002",
        "subject": "苏婉清",
        "predicate": "是朋友",
        "object": "林晨",
        "entity_type": "character",
        "importance": "secondary",
        "note": "重要配角"
    },
    {
        "id": "char-003",
        "subject": "钱老",
        "predicate": "是师父",
        "object": "林晨",
        "entity_type": "character",
        "importance": "secondary",
        "note": "引路人"
    }
]

# 测试数据：地点三元组
location_triples = [
    {
        "id": "loc-001",
        "subject": "江城",
        "predicate": "是",
        "object": "都市",
        "entity_type": "location",
        "location_type": "city",
        "importance": "core",
        "note": "故事主要发生地"
    },
    {
        "id": "loc-002",
        "subject": "云顶山庄",
        "predicate": "位于",
        "object": "江城",
        "entity_type": "location",
        "location_type": "building",
        "importance": "important",
        "note": "重要场景"
    },
    {
        "id": "loc-003",
        "subject": "清风观",
        "predicate": "位于",
        "object": "江城",
        "entity_type": "location",
        "location_type": "building",
        "importance": "important",
        "note": "玄学相关地点"
    }
]

def test_update_knowledge():
    """测试更新知识图谱"""
    url = f"{BASE_URL}/novels/{NOVEL_ID}/knowledge"

    # 获取当前知识
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ 获取知识失败: {response.status_code}")
        return

    current = response.json()
    print(f"✓ 当前三元组数量: {len(current['facts'])}")

    # 合并新旧三元组
    all_facts = character_triples + location_triples

    # 更新知识
    payload = {
        "version": current["version"],
        "premise_lock": current["premise_lock"],
        "chapters": current["chapters"],
        "facts": all_facts
    }

    response = requests.put(url, json=payload)
    if response.status_code != 200:
        print(f"❌ 更新知识失败: {response.status_code}")
        print(response.text)
        return

    updated = response.json()
    print(f"✓ 更新后三元组数量: {len(updated['facts'])}")

    # 验证新字段
    print("\n人物三元组:")
    for fact in updated['facts']:
        if fact.get('entity_type') == 'character':
            print(f"  - {fact['subject']} ({fact['importance']}): {fact['predicate']} -> {fact['object']}")

    print("\n地点三元组:")
    for fact in updated['facts']:
        if fact.get('entity_type') == 'location':
            loc_type = fact.get('location_type', 'unknown')
            print(f"  - {fact['subject']} [{loc_type}] ({fact['importance']}): {fact['predicate']} -> {fact['object']}")

    print("\n✅ 测试完成！")

if __name__ == "__main__":
    test_update_knowledge()
