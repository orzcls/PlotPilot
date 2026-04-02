#!/usr/bin/env python3
"""
Check chapter generation progress
"""
import sys
import json
import os
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

NOVEL_DIR = Path("data/novels/novel-1775066530753/chapters")

def check_progress(max_chapter=100):
    """Check which chapters are completed"""
    completed = []
    total_words = 0

    for i in range(1, max_chapter + 1):
        chapter_file = NOVEL_DIR / f"novel-1775066530753-chapter-{i}.json"
        if chapter_file.exists():
            try:
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    word_count = data.get('word_count', 0)
                    if word_count > 0:
                        completed.append(i)
                        total_words += word_count
            except:
                pass

    print(f"✅ Completed: {len(completed)}/{max_chapter} chapters")
    print(f"📝 Total words: {total_words:,}")
    print(f"📊 Average: {total_words // len(completed) if completed else 0} words/chapter")
    print()

    if completed:
        print(f"Chapters: {min(completed)}-{max(completed)}")

        # Find gaps
        gaps = []
        for i in range(min(completed), max(completed)):
            if i not in completed:
                gaps.append(i)

        if gaps:
            print(f"⚠️  Missing: {gaps}")
        else:
            print("✓ No gaps in sequence")

    return completed, total_words

if __name__ == "__main__":
    max_ch = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    check_progress(max_ch)
