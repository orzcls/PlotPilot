#!/usr/bin/env python3
"""
Batch chapter generation with error handling and retry logic
"""
import sys
import time
import requests
from datetime import datetime

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8007"
NOVEL_SLUG = "novel-1775066530753"

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")
    sys.stdout.flush()

def generate_chapters(start, end, max_retries=3):
    """Generate chapters with retry logic"""
    log(f"Starting batch generation: chapters {start}-{end}")

    for chapter_num in range(start, end + 1):
        log(f"Chapter {chapter_num} starting...")

        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                url = f"{BASE_URL}/api/workflow/hosted-write-stream"
                params = {
                    "slug": NOVEL_SLUG,
                    "from_chapter": chapter_num,
                    "to_chapter": chapter_num,
                    "auto_save": "true",
                    "auto_outline": "true"
                }

                response = requests.get(url, params=params, stream=True, timeout=600)

                if response.status_code != 200:
                    log(f"  ERROR: HTTP {response.status_code}")
                    retry_count += 1
                    if retry_count < max_retries:
                        log(f"  Retrying in 5 seconds... (attempt {retry_count + 1}/{max_retries})")
                        time.sleep(5)
                    continue

                # Process SSE stream
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            data_str = line_str[6:]
                            if data_str.strip() and data_str != '[DONE]':
                                try:
                                    import json
                                    event = json.loads(data_str)
                                    if event.get('type') == 'done':
                                        log(f"  Chapter {chapter_num} completed!")
                                        success = True
                                        break
                                    elif event.get('type') == 'error':
                                        log(f"  ERROR: {event.get('message', 'Unknown error')}")
                                        break
                                except json.JSONDecodeError:
                                    pass

                if success:
                    break
                else:
                    retry_count += 1
                    if retry_count < max_retries:
                        log(f"  Retrying in 10 seconds... (attempt {retry_count + 1}/{max_retries})")
                        time.sleep(10)

            except requests.exceptions.Timeout:
                log(f"  ERROR: Request timeout")
                retry_count += 1
                if retry_count < max_retries:
                    log(f"  Retrying in 10 seconds... (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(10)
            except Exception as e:
                log(f"  ERROR: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    log(f"  Retrying in 10 seconds... (attempt {retry_count + 1}/{max_retries})")
                    time.sleep(10)

        if not success:
            log(f"  FAILED after {max_retries} attempts. Stopping.")
            return False

        # Small delay between chapters
        if chapter_num < end:
            time.sleep(2)

    log(f"Batch complete: chapters {start}-{end}")
    return True

if __name__ == "__main__":
    start_chapter = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    end_chapter = int(sys.argv[2]) if len(sys.argv) > 2 else 20

    log("=" * 60)
    log(f"Batch Chapter Generation: {start_chapter}-{end_chapter}")
    log("=" * 60)

    success = generate_chapters(start_chapter, end_chapter)

    if success:
        log("=" * 60)
        log("Generation Complete!")
        log("=" * 60)
        sys.exit(0)
    else:
        log("=" * 60)
        log("Generation Failed")
        log("=" * 60)
        sys.exit(1)
