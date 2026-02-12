import os
import re
import tkinter as tk
from tkinter import filedialog

# --- 設定 ---
# 削除対象のディレクトリ (ここは固定のままでOK)
TARGET_DIR = "J:\\"

# --- ロジック ---

def main():
    print("--- Text Dump File Remover ---")
    
    # 1. ファイル選択ダイアログを表示
    # Tkinterのルートウィンドウを作成し、すぐに隠す（ダイアログだけ見せるため）
    root = tk.Tk()
    root.withdraw()

    print("ポップアップウィンドウでログファイルを選択してください...")
    
    log_file_path = filedialog.askopenfilename(
        title="Teraboxのファイル名リスト(txt)を選択してください",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        initialdir=os.getcwd() # カレントディレクトリから開始
    )

    # キャンセルされた場合
    if not log_file_path:
        print("ファイル選択がキャンセルされました。終了します。")
        return

    print(f"読み込み対象: {log_file_path}")

    # 2. ファイル読み込み
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(log_file_path, "r", encoding="cp932") as f: # Shift-JIS対策
                content = f.read()
        except Exception as e:
            print(f"ファイル読み込みエラー: {e}")
            return

    # 行ごとに分割して処理
    lines = content.splitlines()
    
    print(f"リスト読み込み完了: {len(lines)} 行")
    print("-" * 60)

    deleted_count = 0
    not_found_count = 0

    for line in lines:
        filename = line.strip()
        
        # 空行や関係ない行をスキップ
        if "Fall Guys" not in filename or not filename.endswith(".mp4"):
            continue

        # Terabox上のファイル名がそのままJドライブにあるか確認
        full_path = os.path.join(TARGET_DIR, filename)
        
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"[削除成功] {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"[削除エラー] {filename}: {e}")
        else:
            # 見つからない場合、数字(16桁)だけ抜き出して曖昧検索
            if try_fuzzy_delete_by_digits(TARGET_DIR, filename):
                deleted_count += 1
            else:
                # print(f"[未検出] {filename}")
                not_found_count += 1

    print("-" * 60)
    print(f"削除合計: {deleted_count} 件")
    if not_found_count > 0:
        print(f"見つからなかったファイル: {not_found_count} 件")

def try_fuzzy_delete_by_digits(target_dir, text_filename):
    """
    ファイル名が完全一致しない場合、数字16桁だけを使って削除を試みる
    """
    digits = "".join(re.findall(r'\d', text_filename))
    
    if len(digits) != 16:
        return False
        
    year, month, day = digits[0:4], digits[4:6], digits[6:8]
    hour, minute, second, ms = digits[8:10], digits[10:12], digits[12:14], digits[14:16]
    
    candidates = [
        f"Fall Guys {year}.{month}.{day} - {hour}.{minute}.{second}.{ms}.mp4",
        f"Fall Guys {year}.{month}.{day} - {hour}.{minute}.{second}.{ms}_Trim.mp4"
    ]
    
    for fname in candidates:
        full_path = os.path.join(target_dir, fname)
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                print(f"[削除成功(補正)] {fname}")
                return True
            except:
                pass
    return False

if __name__ == "__main__":
    main()