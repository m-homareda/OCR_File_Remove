import pytesseract
from PIL import Image, ImageGrab
import os
import re
import itertools

# --- 設定 ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TARGET_DIR = "J:\\"
MAX_FLIPS = 2

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
    """数字列からファイル名パスを生成"""
    year, month, day = digits[0:4], digits[4:6], digits[6:8]
    hour, minute, second, ms = digits[8:10], digits[10:12], digits[12:14], digits[14:16]
    base = f"Fall Guys {year}.{month}.{day} - {hour}.{minute}.{second}.{ms}"
    return base + "_Trim.mp4" if is_trim else base + ".mp4"

def main():
    print("クリップボードから画像を読み込んでいます...")
    img = ImageGrab.grabclipboard()
    if not isinstance(img, Image.Image):
        print("エラー: クリップボードに画像がありません。")
        return

    try:
        raw_text = pytesseract.image_to_string(img, lang='eng')
        
        # ★ここだけ追加・変更★
        # OCR結果から邪魔な記号（. , ' " _）を消す
        cleaned_text = re.sub(r"[.,'\"_]", "", raw_text)
        # O -> 0 変換
        cleaned_text = cleaned_text.replace('O', '0').replace('o', '0')
        
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
            # 桁数が合わないものは、無理に解釈せずスキップしてログを出す
            # (変に削ると誤削除のリスクがあるため)
            print(f"[解析失敗] 桁数不一致 ({len(ocr_digits)}桁): {line.strip()}")
            continue

        is_trim = "T" in line or "m" in line or "Trim" in line
        candidate_digits_list = get_38_variations(ocr_digits)
        file_deleted = False

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