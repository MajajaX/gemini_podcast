# YouTube Gemini 財經重點摘要工具

自動下載 YouTube 影片，轉換為音檔，使用 Gemini API 分析並提取科技、經濟、財金、股票重點，輸出繁體中文摘要。

## 功能

- 下載 YouTube 影片音訊
- 使用 Gemini API 分析音訊內容
- 自動提取科技、經濟、財金、股票相關重點
- 輸出繁體中文 Markdown 摘要到 docs 資料夾

## 安裝

### 1. 安裝必要軟體

**Windows:**
```bash
# 安裝 ffmpeg（使用 chocolatey）
choco install ffmpeg

# 或手動安裝：
# 1. 下載 https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
# 2. 解壓並將 bin 資料夾加入環境變數 PATH
```

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

### 2. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

### 3. 設定 API Key

建立 `.env` 檔案：
```
GEMINI_API_KEY=your_api_key_here
```

或設定環境變數：
```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# macOS/Linux
export GEMINI_API_KEY=your_api_key_here
```

## 使用方法

```bash
python youtube_gemini_summary.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

或直接在腳本中修改 URL：
```python
YOUTUBE_URL = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

## 輸出

摘要文件會儲存在 `docs/` 資料夾中，檔名格式：`summary_YYYYMMDD_HHMMSS.md`

## 模型說明

使用 `gemini-2.0-flash-lite-preview-02-05` 模型，這是 Gemini 的最新輕量級模型，適合快速處理音訊內容。

## 注意事項

- 請確保您有足夠的 Gemini API 配額
- 長影片可能需要較長處理時間
- 音訊檔案會暫時儲存在 `temp_audio/` 資料夾，處理完成後自動清理