import os
import json
from pathlib import Path
from PIL import Image

def main():
    mapping_path = Path('land-1/gallery_mapping.json')
    images_dir = Path('land-1/images')

    with open(mapping_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data['mapping']:
        filename = entry['new_filename']
        img_path = images_dir / filename
        if not img_path.is_file():
            entry['orientation'] = 'unknown'
            continue
        try:
            with Image.open(img_path) as img:
                w, h = img.size
                if w > h:
                    entry['orientation'] = 'landscape'
                elif h > w:
                    entry['orientation'] = 'portrait'
                else:
                    entry['orientation'] = 'square'
        except Exception as e:
            entry['orientation'] = 'error'

    with open(mapping_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
