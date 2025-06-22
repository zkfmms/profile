# -*- coding: utf-8 -*-
import os
import re
import io
import sys

try:
    from PIL import Image
except ImportError:
    print("エラー: Pillowライブラリが見つかりません。")
    print("このプログラムを実行するには、まずPillowをインストールする必要があります。")
    print("ターミナル（コマンドプロンプト）で以下のコマンドを実行してください:")
    print("pip install Pillow")
    sys.exit()

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    # HEICファイルがなくても動作は継続できるように、ここでは警告に留める
    print("情報: pillow-heifライブラリが見つかりません。HEICファイルの変換はスキップされます。")
    print("HEICファイルも変換したい場合は、`pip install pillow-heif` を実行してください。")
    pillow_heif = None

# --- 設定 ---
# 実行ディレクトリ (このスクリプトを置いた場所)
TARGET_DIR = '.'
# リサイズ後の最大辺の長さ (px)
MAX_DIMENSION = 1000
# 対象ファイルの拡張子 (小文字で指定)
SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.heic')
# ファイル名の先頭をチェックする正規表現 (全角数字)
FILENAME_PATTERN = re.compile(r'^[０-９]')


def find_target_images(directory: str, extensions: tuple) -> list[str]:
    """指定されたディレクトリから対象画像を検索する"""
    target_files = []
    try:
        for filename in os.listdir(directory):
            # ファイルであり、指定の拡張子で、正規表現にマッチするかをチェック
            if (os.path.isfile(os.path.join(directory, filename)) and
                    filename.lower().endswith(extensions) and
                    FILENAME_PATTERN.match(filename)):
                target_files.append(filename)
    except FileNotFoundError:
        print(f"エラー: ディレクトリ '{directory}' が見つかりません。")
        return []
    return sorted(target_files)


def convert_heic_to_jpg(heic_path: str) -> str | None:
    """HEICファイルをJPGに変換し、元のファイルを削除する"""
    if not pillow_heif:
        print(f"⚠️  '{heic_path}' はHEICファイルですが、ライブラリがないためスキップします。")
        return None

    # 出力ファイルパスを生成 (例: file.heic -> file.jpg)
    jpg_path = os.path.splitext(heic_path)[0] + '.jpg'

    if os.path.exists(jpg_path):
        print(f"🔵 '{jpg_path}' は既に存在するため、HEICからの変換をスキップします。")
        # 変換先が既にある場合、元のHEICを削除
        os.remove(heic_path)
        print(f"🗑️  重複する元のファイル '{heic_path}' を削除しました。")
        return jpg_path

    try:
        print(f"🔄 '{heic_path}' をJPGに変換中...")
        img = Image.open(heic_path)

        # HEIFのメタデータが原因で保存に失敗することがあるため、
        # RGBモードの新しいImageオブジェクトにピクセルデータを貼り付ける
        img_rgb = Image.new("RGB", img.size)
        img_rgb.paste(img)

        img_rgb.save(jpg_path, 'JPEG', quality=95) # 初期品質は高めに設定
        print(f"✅ '{heic_path}' -> '{jpg_path}' に変換しました。")
        os.remove(heic_path) # 変換に成功したら元のHEICを削除
        print(f"🗑️  元のファイル '{heic_path}' を削除しました。")
        return jpg_path
    except Exception as e:
        print(f"❌ エラー: '{heic_path}' のJPG変換中にエラーが発生しました: {e}")
        return None


def resize_image(filepath: str):
    """画像の長辺が指定サイズ以下になるようにリサイズし、ファイルを上書き保存する"""
    try:
        img = Image.open(filepath)
        original_width, original_height = img.size

        if original_width <= MAX_DIMENSION and original_height <= MAX_DIMENSION:
            print(f"🔵 '{filepath}' は既に{MAX_DIMENSION}px以下です。スキップします。")
            return

        # アスペクト比を維持して新しいサイズを計算
        if original_width > original_height:
            new_width = MAX_DIMENSION
            new_height = int(original_height * (MAX_DIMENSION / original_width))
        else:
            new_height = MAX_DIMENSION
            new_width = int(original_width * (MAX_DIMENSION / original_height))

        print(f"🔄 '{filepath}' をリサイズ中... ({original_width}x{original_height} -> {new_width}x{new_height})")

        # 高品質なリサイズフィルタ(LANCZOS)を使用
        # Pillow 9.1.0以降で推奨される方法
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # JPEGはアルファチャンネルをサポートしないため、RGBに変換
        if resized_img.mode in ('RGBA', 'P'):
            resized_img = resized_img.convert('RGB')

        # ファイルを上書き保存。品質は高めに設定。
        resized_img.save(filepath, 'JPEG', quality=95, optimize=True)
        print(f"✅ '{filepath}' をリサイズしました。")

    except Exception as e:
        print(f"❌ エラー: '{filepath}' の処理中にエラーが発生しました: {e}")


def main():
    """メイン処理"""
    print("--- 全角数字で始まる画像ファイルの検索 ---")
    # HEICとJPG/JPEGの両方を検索
    initial_target_files = find_target_images(TARGET_DIR, SUPPORTED_EXTENSIONS)

    if not initial_target_files:
        print("対象となる画像ファイルが見つかりませんでした。")
        print(f"条件: ファイル名が全角数字で始まり、拡張子が {SUPPORTED_EXTENSIONS} のファイル")
        return

    print("\n以下のファイルが見つかりました:")
    for img_file in initial_target_files:
        print(f"- {img_file}")

    # ユーザーに実行確認
    try:
        prompt = f"\nこれらのファイルを処理しますか？ (HEICはJPGに変換後、JPGは長辺が{MAX_DIMENSION}px以下にリサイズされます) (y/n): "
        answer = input(prompt).lower()
        if answer != 'y':
            print("処理を中止しました。")
            return
    except (EOFError, KeyboardInterrupt):
        print("\n処理を中止しました。")
        return

    # --- ステップ1: HEICからJPGへの変換 ---
    heic_files = [f for f in initial_target_files if f.lower().endswith('.heic')]
    if heic_files:
        print("\n--- HEICからJPGへの変換処理を開始します ---")
        for filename in heic_files:
            filepath = os.path.join(TARGET_DIR, filename)
            convert_heic_to_jpg(filepath)
    else:
        print("\n--- HEICファイルは見つかりませんでした ---")


    # --- ステップ2: JPGのリサイズ ---
    # HEICから変換されたファイルも含めて、JPG/JPEGファイルを再検索
    jpg_files_to_process = find_target_images(TARGET_DIR, ('.jpg', '.jpeg'))

    if jpg_files_to_process:
        print("\n--- JPG画像のリサイズ処理を開始します ---")
        for filename in jpg_files_to_process:
            filepath = os.path.join(TARGET_DIR, filename)
            resize_image(filepath)
    else:
        print("\n--- リサイズ対象のJPG画像は見つかりませんでした ---")

    print("\n--- 全ての処理が完了しました ---")


if __name__ == "__main__":
    main()