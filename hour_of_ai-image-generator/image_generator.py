#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hour of AI - Image Generator
使用 Gemini 3.1 Flash Image Preview 模型生成圖片
"""

import os
import sys
import io
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image as PILImage

# 載入環境變數
dotenv_path = Path(__file__).parent.parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# 設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "gemini-3.1-flash-image-preview"
OUTPUT_DIR = Path(__file__).parent / "generated_images"
ASPECT_RATIO = "1:1"
IMAGE_SIZE = "512"


def ensure_directories():
    """確保輸出資料夾存在"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"✓ 輸出資料夾: {OUTPUT_DIR}")


def validate_api_key():
    """檢查 API Key 是否設定"""
    if not GEMINI_API_KEY:
        print("✗ 錯誤: 請設定 GEMINI_API_KEY 環境變數")
        print("請在專案根目錄建立 .env 檔案並加入:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    return True


def get_image_size(image: types.Image) -> tuple[int, int] | None:
    """取得 google.genai Image 的實際像素尺寸。"""
    if not image.image_bytes:
        return None

    with PILImage.open(io.BytesIO(image.image_bytes)) as pil_image:
        return pil_image.size


def generate_image(prompt: str) -> types.Image:
    """
    使用 Gemini API 生成圖片

    Args:
        prompt: 圖片提示詞

    Returns:
        google.genai.types.Image: 生成的圖片
    """
    print(f"\n正在生成圖片...")
    print(f"模型: {MODEL_ID}")
    print(f"提示詞: {prompt}")

    # 初始化 Gemini 客戶端
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 設定生成配置，啟用圖片輸出
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=ASPECT_RATIO,
            image_size=IMAGE_SIZE,
        ),
    )

    # 生成內容
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=prompt,
        config=config,
    )

    # 解析回應，提取圖片資料
    text_response = None
    generated_image = None

    for part in response.parts:
        if getattr(part, "thought", False):
            continue

        if part.inline_data is not None:
            image = part.as_image()
            generated_image = image
        elif part.text is not None:
            text_response = part.text

    if generated_image is None:
        raise ValueError("未收到圖片資料，回應內容: " + (text_response or "無文字回應"))

    print(f"✓ 圖片生成完成")
    print(f"  圖片比例: {ASPECT_RATIO}")
    print(f"  輸出尺寸設定: {IMAGE_SIZE}")
    actual_size = get_image_size(generated_image)
    if actual_size is not None:
        print(f"  原始尺寸: {actual_size}")

    return generated_image


def save_image(image: types.Image, prompt: str) -> Path:
    """
    儲存圖片到輸出資料夾

    Args:
        image: PIL Image 物件
        prompt: 生成提示詞（用於 metadata）

    Returns:
        Path: 儲存的檔案路徑
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"image_{timestamp}.png"
    filepath = OUTPUT_DIR / filename

    # 儲存圖片
    image.save(str(filepath))

    print(f"✓ 圖片已儲存: {filepath}")

    return filepath


def main():
    """主程式"""
    print("=" * 60)
    print("🎨 Hour of AI - Image Generator")
    print("=" * 60)

    # 確保資料夾存在
    ensure_directories()

    # 檢查 API Key
    if not validate_api_key():
        sys.exit(1)

    # 取得提示詞
    if len(sys.argv) > 1:
        # 從命令列參數取得
        prompt = " ".join(sys.argv[1:])
    else:
        # 互動式輸入
        prompt = input("\n請輸入圖片提示詞: ").strip()

    if not prompt:
        print("✗ 未輸入提示詞，程式結束。")
        sys.exit(1)

    try:
        # 生成圖片
        image = generate_image(prompt)

        # 儲存圖片
        output_path = save_image(image, prompt)

        print(f"\n{'=' * 60}")
        print("🎉 完成！")
        print(f"圖片檔案: {output_path}")
        print(f"{'=' * 60}\n")

    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
