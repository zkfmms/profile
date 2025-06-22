import os
import re
import shutil
import json
from pathlib import Path

# 全角数字を半角数字に変換する関数
def zenkaku_to_hankaku_digit(text: str) -> str:
    return text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))

def run_rename_and_extract():
    image_dir_path = Path('/Users/rosenthal/Documents/GitHub/profile/land-1/images')
    output_json_path = Path('/Users/rosenthal/Documents/GitHub/profile/land-1/gallery_mapping.json')
    
    if not image_dir_path.is_dir():
        error_message = {"error": f"Directory not found: {image_dir_path}", "mapping": []}
        try:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(error_message, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing error JSON to file: {e}")
        print(json.dumps(error_message, indent=2, ensure_ascii=False))
        return

    files_to_process = []
    for ext in ('*.jpg', '*.jpeg'): # Glob patterns are case-sensitive on some systems by default
        files_to_process.extend(list(image_dir_path.glob(ext)))
        files_to_process.extend(list(image_dir_path.glob(ext.upper()))) # Add uppercase extensions

    # Remove duplicates if any (e.g. if globbing '*.jpg' and '*.JPG' returns the same file on case-insensitive FS)
    files_to_process = sorted(list(set(files_to_process)), key=lambda p: p.name)


    mapping_data = []
    
    for original_file_path in files_to_process:
        original_filename = original_file_path.name
        
        # Pattern: 全角数字、タイトル名.拡張子 (拡張子はjpg, jpeg, JPG, JPEG)
        # Example: １０、愛ノ壁ヲブチ壊セ。.jpg
        match = re.match(r"^([０-９〇一二三四五六七八九十百千拾萬億兆京]+)[、，](.+?)\.(jpe?g)$", original_filename, re.IGNORECASE) # Expanded character sets
        
        if match:
            zenkaku_num_str = match.group(1)
            title = match.group(2).strip() 
            extension = match.group(3) # This will capture jpg, jpeg (actual case from filename due to IGNORECASE)
            
            hankaku_num_str = zenkaku_to_hankaku_digit(zenkaku_num_str)
            
            new_filename = f"{hankaku_num_str}.{extension}"
            new_filepath = image_dir_path / new_filename
            
            try:
                if original_file_path.resolve() == new_filepath.resolve():
                    mapping_data.append({
                        "original_filename": original_filename,
                        "new_filename": new_filename,
                        "title": title,
                        "status": "Skipped - No change needed (already named correctly)."
                    })
                else:
                    # Perform the rename, overwriting if new_filepath exists
                    original_file_path.rename(new_filepath)
                    mapping_data.append({
                        "original_filename": original_filename,
                        "new_filename": new_filename,
                        "title": title,
                        "status": "Renamed"
                    })

            except Exception as e:
                mapping_data.append({
                    "original_filename": original_filename,
                    "new_filename": f"ERROR_RENAMING_TO_{new_filename}",
                    "title": title,
                    "error": str(e)
                })
        else:
            # File does not match the pattern "全角数字、タイトル名.拡張子"
            # Add to mapping data with a note that it was skipped.
            mapping_data.append({
                "original_filename": original_filename,
                "status": "Skipped - Pattern not matched."
            })


    # Save results to JSON file
    try:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump({"mapping": mapping_data}, f, indent=2, ensure_ascii=False)
        print(f"Processing complete. Results saved to {output_json_path}")
        # Print mapping to stdout as well for the agent to see
        print(json.dumps({"mapping": mapping_data}, indent=2, ensure_ascii=False))
    except Exception as e:  # Corrected line
        print(f"Error writing JSON output to file: {e}")
        # Still print to stdout if file writing fails
        print(json.dumps({"error": f"Error writing JSON output to file: {e}", "mapping": mapping_data}, indent=2, ensure_ascii=False))

def run_actual_rename_based_on_mapping():
    image_dir_path = Path('/Users/rosenthal/Documents/GitHub/profile/land-1/images')
    mapping_json_path = Path('/Users/rosenthal/Documents/GitHub/profile/land-1/gallery_mapping.json')
    
    rename_log = []

    if not mapping_json_path.is_file():
        message = f"Error: Mapping file not found at {mapping_json_path}"
        print(message)
        print(json.dumps({"status": "Error", "message": message, "log": rename_log}, indent=2, ensure_ascii=False))
        return

    try:
        with open(mapping_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "mapping" not in data or not isinstance(data["mapping"], list):
            message = "Error: JSON mapping data is missing or not a list."
            print(message)
            print(json.dumps({"status": "Error", "message": message, "log": rename_log}, indent=2, ensure_ascii=False))
            return
            
        mapping_entries = data["mapping"]
    except Exception as e:
        message = f"Error reading or parsing mapping JSON: {e}"
        print(message)
        print(json.dumps({"status": "Error", "message": message, "log": rename_log}, indent=2, ensure_ascii=False))
        return

    if not mapping_entries:
        message = "No mapping entries found in JSON file."
        print(message)
        print(json.dumps({"status": "Info", "message": message, "log": rename_log}, indent=2, ensure_ascii=False))
        return

    print(f"Starting rename process. Image directory: {image_dir_path}")
    for entry in mapping_entries:
        original_filename = entry.get("original_filename")
        new_filename = entry.get("new_filename")

        if not original_filename or not new_filename:
            log_entry = {
                "original": original_filename or "N/A",
                "new": new_filename or "N/A",
                "status": "Skipped - Missing original or new filename in mapping."
            }
            rename_log.append(log_entry)
            print(f"Skipping entry: Original: '{log_entry['original']}', New: '{log_entry['new']}' due to missing info.")
            continue

        original_file_path = image_dir_path / original_filename
        new_file_path = image_dir_path / new_filename

        log_item = {
            "original_filename": original_filename,
            "new_filename": new_filename,
            "original_full_path": str(original_file_path),
            "new_full_path": str(new_file_path),
        }

        if not original_file_path.is_file():
            log_item["status"] = "Skipped - Original file not found."
            print(f"Original file not found: {original_file_path}")
        elif original_file_path.resolve() == new_file_path.resolve():
            log_item["status"] = "Skipped - No change needed (already named correctly)."
            print(f"No change needed for: {original_filename} (already {new_filename})")
        else:
            try:
                original_file_path.rename(new_file_path)
                log_item["status"] = "Renamed successfully."
                print(f"Renamed: '{original_filename}' -> '{new_filename}'")
            except FileExistsError:
                log_item["status"] = f"Skipped - Destination file already exists: {new_file_path}"
                print(f"Destination file '{new_filename}' already exists. Skipping rename for '{original_filename}'.")
            except Exception as e:
                log_item["status"] = f"Error renaming: {e}"
                print(f"Error renaming '{original_filename}' to '{new_filename}': {e}")
        
        rename_log.append(log_item)

    final_status_message = "File renaming process complete based on mapping JSON."
    print(final_status_message)
    # Output the full log as JSON for the agent to inspect
    print(json.dumps({"status": "Completed", "message": final_status_message, "log": rename_log}, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    run_rename_and_extract()
    run_actual_rename_based_on_mapping()
