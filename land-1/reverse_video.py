import os
import subprocess

# 元の動画ファイルのパス
input_path = "video/background.mp4"
# 出力ファイルのパス
output_path = "video/background_reversed.mp4"
# バックアップファイルのパス
backup_path = "video/background_original.mp4"

# 元のファイルをバックアップ
if not os.path.exists(backup_path):
    print(f"元の動画をバックアップ: {backup_path}")
    os.rename(input_path, backup_path)
else:
    print(f"バックアップ {backup_path} は既に存在します")

# FFMPEGを使用して動画を逆再生する
print("FFMPEGを使用して動画を逆再生しています...")
cmd = [
    "ffmpeg", 
    "-i", backup_path, 
    "-vf", "reverse", 
    "-af", "areverse", 
    "-preset", "fast", 
    "-y",  # 既存のファイルを上書き
    input_path
]

try:
    subprocess.run(cmd, check=True)
    print("完了しました！")
except subprocess.CalledProcessError as e:
    print(f"エラーが発生しました: {e}")