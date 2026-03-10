#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Gemini 財經重點摘要工具
自動下載 YouTube 影片，轉換為音檔，使用 Gemini API 分析並提取重點
"""

import os
import sys
import re
import time
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 載入環境變數
load_dotenv()

# 設定
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_ID = "gemini-3.1-flash-lite-preview"  # 最新輕量級模型
OUTPUT_DIR = Path("docs")
TEMP_DIR = Path("temp_audio")


def sanitize_filename(name, max_length=60):
    """
    將字串轉為合法的檔案名稱
    """
    # 移除 Windows/Unix 不允許的字元
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    # 將空白與特殊符號換成底線
    name = re.sub(r'[\s]+', '_', name).strip('_')
    return name[:max_length]


def ensure_directories():
    """確保必要的資料夾存在"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)


def download_audio(youtube_url):
    """
    使用 yt-dlp 下載 YouTube 影片音訊
    """
    print(f"正在下載音訊: {youtube_url}")

    # 產生暫時檔案名稱
    temp_filename = f"youtube_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    temp_path = TEMP_DIR / temp_filename

    # yt-dlp 指令，優先下載 webm（Gemini 原生支援，不需 ffmpeg）
    ydl_opts = [
        "yt-dlp",
        "-f",
        "bestaudio[ext=webm]/bestaudio[ext=opus]/bestaudio",
        "-o",
        str(temp_path) + ".%(ext)s",
        youtube_url,
    ]

    try:
        result = subprocess.run(ydl_opts, capture_output=True, text=True, check=True)

        # 找到下載的檔案
        downloaded_files = list(TEMP_DIR.glob(f"{temp_filename}*"))
        if downloaded_files:
            audio_path = downloaded_files[0]
            print(f"✓ 音訊下載完成: {audio_path}")
            return str(audio_path)
        else:
            raise FileNotFoundError("找不到下載的音訊檔案")

    except subprocess.CalledProcessError as e:
        print(f"✗ 下載失敗: {e}")
        print(f"錯誤訊息: {e.stderr}")
        raise


def get_video_info(youtube_url):
    """
    取得 YouTube 影片資訊
    """
    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--print",
                "%(title)s",
                "--print",
                "%(uploader)s",
                "--print",
                "%(duration>%H:%M:%S)s",
                youtube_url,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        lines = result.stdout.strip().split("\n")
        return {
            "title": lines[0] if len(lines) > 0 else "Unknown",
            "uploader": lines[1] if len(lines) > 1 else "Unknown",
            "duration": lines[2] if len(lines) > 2 else "Unknown",
        }
    except:
        return {"title": "Unknown", "uploader": "Unknown", "duration": "Unknown"}


def analyze_with_gemini(audio_path):
    """
    使用 Gemini API 分析音訊內容
    """
    if not GEMINI_API_KEY:
        raise ValueError("請設定 GEMINI_API_KEY 環境變數")

    print(f"\n正在使用 Gemini API 分析音訊...")
    print(f"模型: {MODEL_ID}")

    # 初始化 Gemini 客戶端
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 上傳音訊檔案（明確指定 MIME type，避免 webm 被誤判為影片）
    print("上傳音訊檔案中...")
    ext = Path(audio_path).suffix.lower()
    mime_map = {
        ".webm": "audio/webm",
        ".opus": "audio/opus",
        ".ogg":  "audio/ogg",
        ".m4a":  "audio/mp4",
        ".mp3":  "audio/mpeg",
        ".wav":  "audio/wav",
    }
    mime_type = mime_map.get(ext, "audio/webm")
    print(f"  格式: {ext}，MIME: {mime_type}")
    audio_file = client.files.upload(
        file=audio_path,
        config={"mime_type": mime_type},
    )
    print(f"✓ 音訊上傳完成，等待處理...")

    # 等待檔案變為 ACTIVE 狀態（相容新舊 SDK 的 state 格式）
    for _ in range(30):
        state = audio_file.state
        state_str = state.name if hasattr(state, "name") else str(state)
        if state_str == "ACTIVE":
            break
        if state_str == "FAILED":
            raise ValueError("檔案處理失敗")
        print("  檔案處理中，請稍候...")
        time.sleep(3)
        audio_file = client.files.get(name=audio_file.name)
    else:
        raise ValueError("等待逾時，檔案未能進入 ACTIVE 狀態")

    state = audio_file.state
    state_str = state.name if hasattr(state, "name") else str(state)
    if state_str != "ACTIVE":
        raise ValueError(f"檔案處理失敗，狀態: {state_str}")

    print(f"✓ 檔案已就緒")

    # 設定提示詞
    prompt = """請仔細聆聽這段音訊，針對以下四個主題，提供詳細的重點整理。

主題範圍：
1. **科技** - 新技術、產品發布、科技趨勢、AI、半導體、軟硬體產業動態等
2. **經濟** - 總體經濟數據、市場趨勢、貨幣政策、通膨、就業、GDP 等
3. **財金** - 金融政策、央行決策、銀行業動態、投資理財、外匯、債券等
4. **股票** - 個股深度分析、股市趨勢、法人動向、投資建議、財報數據、產業輪動等
5. **地緣政治** - 國際衝突、軍事動態、制裁、外交關係、貿易戰、區域安全等
6. **國際局勢** - 大國博弈、政權更迭、國際組織動向、峰會、條約協議等
7. **重要新聞** - 其他對市場或社會有重大影響的國際時事

請忽略與上述主題無關的內容。

整理原則：
- 每個重點必須包含具體數據、人名、公司名稱、事件背景等細節，不得流於概括
- 若討論到某個觀點或預測，需說明依據與邏輯
- 若提到多個面向，請逐一條列，不要合併
- 重要數字、比例、時間點請特別標出（可用粗體）
- 如果有提到後續觀察重點或風險因素，請列在各區塊末尾的「⚠ 風險／待觀察」小節

輸出格式：
- 使用繁體中文
- 使用 Markdown 格式
- 分為「科技重點」、「經濟重點」、「財金重點」、「股票重點」、「地緣政治重點」、「國際局勢重點」、「重要新聞」七個區塊
- 每個重點以條列式呈現（`-`），子項目用縮排（`  -`）
- 如果音訊中沒有該主題的內容，請標註「無相關內容」"""

    # 生成內容（加上 retry 應對 500 暫時性錯誤）
    print("正在分析音訊內容（這可能需要幾分鐘）...")
    last_error = None
    for attempt in range(1, 4):
        try:
            response = client.models.generate_content(
                model=MODEL_ID,
                contents=[prompt, audio_file],
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=8192),
            )
            print("✓ 分析完成")
            return response.text
        except Exception as e:
            last_error = e
            if "500" in str(e) or "INTERNAL" in str(e):
                print(f"  第 {attempt} 次嘗試失敗（500 錯誤），{5 * attempt} 秒後重試...")
                time.sleep(5 * attempt)
            else:
                raise
    raise last_error


def clean_temp_files(audio_path):
    """
    清理暫存檔案
    """
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"✓ 已清理暫存檔案")
    except Exception as e:
        print(f"⚠ 清理暫存檔案時發生錯誤: {e}")


def save_summary(content, video_info, youtube_url):
    """
    儲存摘要到 docs 資料夾
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    title_slug = sanitize_filename(video_info["title"])
    filename = f"{title_slug}_{timestamp}.md"
    filepath = OUTPUT_DIR / filename

    # 建立 Markdown 內容
    md_content = f"""# 📊 財經重點摘要

## 影片資訊

- **標題**: {video_info["title"]}
- **頻道**: {video_info["uploader"]}
- **長度**: {video_info["duration"]}
- **來源**: [{youtube_url}]({youtube_url})
- **分析時間**: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
- **使用模型**: `{MODEL_ID}`

---

## 重點整理

{content}

---

*此摘要由 AI 自動生成，僅供參考。投資有風險，決策需謹慎。*
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n✓ 摘要已儲存: {filepath}")
    return filepath


def main():
    """
    主程式
    """
    # 檢查命令列參數
    if len(sys.argv) < 2:
        youtube_url = input("請輸入 YouTube 網址: ").strip()
        if not youtube_url:
            print("✗ 未輸入網址，程式結束。")
            sys.exit(1)
    else:
        youtube_url = sys.argv[1]

    # 驗證 URL
    if not re.match(
        r"^(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/", youtube_url
    ):
        print("✗ 無效的 YouTube URL")
        sys.exit(1)

    # 確保資料夾存在
    ensure_directories()

    # 檢查 API Key
    if not GEMINI_API_KEY:
        print("✗ 錯誤: 請設定 GEMINI_API_KEY 環境變數")
        print("請建立 .env 檔案並加入: GEMINI_API_KEY=your_api_key")
        sys.exit(1)

    try:
        # 取得影片資訊
        print("正在取得影片資訊...")
        video_info = get_video_info(youtube_url)
        print(f"\n影片: {video_info['title']}")
        print(f"頻道: {video_info['uploader']}")
        print(f"長度: {video_info['duration']}\n")

        # 下載音訊
        audio_path = download_audio(youtube_url)

        # 使用 Gemini 分析
        summary = analyze_with_gemini(audio_path)

        # 儲存摘要
        output_path = save_summary(summary, video_info, youtube_url)

        # 清理暫存檔案
        clean_temp_files(audio_path)

        print(f"\n{'=' * 50}")
        print("🎉 完成！")
        print(f"摘要檔案: {output_path}")
        print(f"{'=' * 50}\n")

    except Exception as e:
        print(f"\n✗ 發生錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
