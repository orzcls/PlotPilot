#!/usr/bin/env python3
"""
UI功能测试脚本
"""
import sys
import time
from playwright.sync_api import sync_playwright

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def test_workbench_ui():
    """测试工作台UI功能"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("1. 导航到首页...")
        page.goto("http://localhost:3004")
        time.sleep(2)

        print("2. 点击进入工作台...")
        # 查找并点击书籍卡片
        page.click('text=重生之会计人生')
        time.sleep(3)

        print("3. 检查左侧边栏章节列表...")
        # 检查章节是否显示
        chapters = page.locator('.sidebar .n-list-item')
        count = chapters.count()
        print(f"   找到 {count} 个章节")

        if count > 0:
            # 检查第一个章节
            first_chapter = chapters.first
            title = first_chapter.inner_text()
            print(f"   第一章: {title}")

            print("4. 点击第一章...")
            first_chapter.click()
            time.sleep(2)

            print("5. 检查工作台内容区域...")
            # 检查章节内容是否加载
            editor = page.locator('.chapter-editor')
            if editor.count() > 0:
                print("   ✓ 章节编辑器已显示")

                # 检查章节标题
                chapter_title = page.locator('.editor-title h3')
                if chapter_title.count() > 0:
                    print(f"   ✓ 章节标题: {chapter_title.inner_text()}")

                # 检查字数统计
                word_count = page.locator('text=/字数:/')
                if word_count.count() > 0:
                    print(f"   ✓ {word_count.inner_text()}")
            else:
                print("   ✗ 章节编辑器未显示")

            print("6. 检查右侧边栏...")
            # 检查章节信息卡片
            chapter_info = page.locator('.chapter-info-card')
            if chapter_info.count() > 0:
                print("   ✓ 章节信息卡片已显示")
                info_text = chapter_info.inner_text()
                print(f"   内容: {info_text[:100]}...")
            else:
                print("   ✗ 章节信息卡片未显示")

            print("7. 测试AI审稿按钮...")
            review_btn = page.locator('button:has-text("AI审稿")')
            if review_btn.count() > 0:
                print("   ✓ AI审稿按钮存在")
                if review_btn.is_disabled():
                    print("   - 按钮已禁用（章节无内容）")
                else:
                    print("   - 按钮可用")
            else:
                print("   ✗ AI审稿按钮未找到")
        else:
            print("   ✗ 未找到章节列表")

        print("\n8. 截图保存...")
        page.screenshot(path="D:/CODE/aitext/test_screenshot.png")
        print("   截图已保存: test_screenshot.png")

        print("\n测试完成！按Enter关闭浏览器...")
        input()

        browser.close()

if __name__ == "__main__":
    try:
        test_workbench_ui()
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
