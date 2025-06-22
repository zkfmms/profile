import os
import json
import re

# このスクリプトは land-1 ディレクトリで実行してください
JSON_PATH = "gallery_mapping.json"
IMAGES_DIR = "images"

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

for entry in data["mapping"]:
    old = entry["new_filename"]
    # タイトルからファイル名に使えない文字を除去
    title = re.sub(r'[\\/:*?"<>|]', '', entry["title"])
    new = f"{title}.jpg"
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
