import os
import json
import re

# このスクリプトは land-1 ディレクトリで実行してください
JSON_PATH = "gallery_mapping.json"
IMAGES_DIR = "images"
TARGET_FILES = [
    "index.html",
    os.path.join("css", "styles.css"),
    # 必要に応じて他のHTML/CSSファイルも追加
]

def sanitize_filename(title):
    # ファイル名に使えない文字を除去
    return re.sub(r'[\\/:*?"<>|]', '', title)

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

# 置換マップ作成: { "1.jpg": "タイトル.jpg", ... }
replace_map = {}
for entry in data["mapping"]:
    old = entry["new_filename"]
    title = sanitize_filename(entry["title"])
    new = f"{title}.jpg"
    replace_map[old] = new

# 画像ファイルのリネーム
for old, new in replace_map.items():
    old_path = os.path.join(IMAGES_DIR, old)
    new_path = os.path.join(IMAGES_DIR, new)
    if os.path.exists(old_path):
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print(f"{old} -> {new}")
        else:
            print(f"Skip (already exists): {new}")
    else:
        print(f"Not found: {old}")

# HTML/CSS等の参照部分を一括置換
for file in TARGET_FILES:
    if not os.path.exists(file):
        print(f"Skip (not found): {file}")
        continue
    with open(file, encoding="utf-8") as f:
        text = f.read()
    replaced = text
    for old, new in replace_map.items():
        replaced = replaced.replace(old, new)
    if replaced != text:
        with open(file, "w", encoding="utf-8") as f:
            f.write(replaced)
        print(f"Updated: {file}")
    else:
        print(f"No changes: {file}")
