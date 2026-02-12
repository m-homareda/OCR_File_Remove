import pytesseract
from PIL import Image, ImageGrab
import os
import re
import itertools

# --- 設定 (Environment) ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TARGET_DIR = "J:\\"
MAX_FLIPS = 2  # 3と8の入れ替え許容数

# --- ロジック ---

def get_38_variations(base_digits):
    """ '3' と '8' を入れ替えた候補リストを生成 """
    flippable_indices = [i for i, char in enumerate(base_digits) if char in '38']
    candidates = set()
    candidates.add(base_digits)

    for r in range(1, MAX_FLIPS + 1):
        for indices_to_flip in itertools.combinations(flippable_indices, r):
            temp_list = list(base_digits)
            for idx in indices_to_flip:
                temp_list[idx] = '8' if temp_list[idx] == '3' else '3'
            candidates.add("".join(temp_list))
    return list(candidates)

def construct_filename(digits, is_trim):
    """
    数字列(16桁)から、PC内のファイル名形式を再構築する
    形式: Fall Guys YYYY.MM.DD - HH.MM.SS.ms.mp4
    """
    year, month, day = digits[0:4], digits[4:6], digits[6:8]
    hour, minute, second, ms = digits[8:10], digits[10:12], digits[12:14], digits[14:16]
    
    base = f"Fall Guys {year}.{month}.{day} - {hour}.{minute}.{second}.{ms}"
    
    if is_trim:
        return base + "_Trim.mp4"
    else:
        return base + ".mp4"

def main():
    print("--- Terabox File Remover ---")
    print("クリップボードから画像を読み込んでいます...")
    
    img = ImageGrab.grabclipboard()
    if not isinstance(img, Image.Image):
        print("エラー: クリップボードに画像がありません。")
        print("Teraboxのファイル一覧をスクショ(Win+Shift+S)してから実行してください。")
        return

    try:
        # OCR実行
        raw_text = pytesseract.image_to_string(img, lang='eng')
        
        # 1. 拡張子 (.mp4, ,mp4, mp4など) を正規表現で強力に除去
        text_no_ext = re.sub(r'(?i)mp4', '', raw_text)
        
        # 2. 一般的な誤読修正
        # O -> 0
        cleaned_text = text_no_ext.replace('O', '0').replace('o', '0')
        # 【追加】 L -> 1, I -> 1 (Fall Guysに大文字のLやIは含まれないため安全)
        cleaned_text = cleaned_text.replace('L', '1').replace('I', '1')
        
    except Exception as e:
        print(f"OCRエラー: {e}")
        return

    lines = cleaned_text.split('\n')
    deleted_count = 0
    
    print("-" * 60)

    for line in lines:
        if "Fall Guys" not in line:
            continue
            
        # 数字のみ抽出
        ocr_digits = "".join(re.findall(r'\d', line))
        
        # 桁数チェック
        if len(ocr_digits) != 16:
            print(f"[解析失敗] 桁数不一致 ({len(ocr_digits)}桁): {line.strip()}")
            continue

        # Trim判定
        is_trim = "Trim" in line or "trim" in line

        # 3-8反転候補の生成
        candidate_digits_list = get_38_variations(ocr_digits)
        file_deleted = False

        # 候補ファイルが存在するかチェック
        for digits_variant in candidate_digits_list:
            filename = construct_filename(digits_variant, is_trim)
            full_path = os.path.join(TARGET_DIR, filename)
            
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    print(f"[削除成功] {filename}")
                    
                    if digits_variant != ocr_digits:
                        print(f"          (補正: {ocr_digits} -> {digits_variant})")
                    
                    deleted_count += 1
                    file_deleted = True
                    break 
                except Exception as e:
                    print(f"[削除エラー] {filename}: {e}")
        
        if not file_deleted:
            print(f"[未検出]   {construct_filename(ocr_digits, is_trim)}")

    print("-" * 60)
    print(f"削除合計: {deleted_count} 件")

if __name__ == "__main__":
    main()