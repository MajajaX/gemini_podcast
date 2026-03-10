# 🤖 AI Tools Collection

這是我的個人 AI 工具集合專案，包含各種實用的 AI 小工具。

## 📁 專案結構

```
ai-tools-collection/
├── .env                    # 全域環境變數 (API Keys)
├── .env.example            # 環境變數範例
├── requirements.txt        # 全域依賴
├── README.md              # 本檔案
│
├── podcast-to-doc/        # 🎧 YouTube 財經摘要工具
│   ├── youtube_gemini_summary.py
│   ├── requirements.txt
│   ├── README.md
│   ├── docs/              # 輸出的摘要檔案
│   └── temp_audio/        # 暫存音訊檔案
│
└── hour_of_ai-image-generator/  # 🎨 AI 圖片生成器
    ├── image_generator.py
    ├── requirements.txt
    ├── README.md
    └── generated_images/  # 輸出的圖片
```

## 🚀 快速開始

### 1. 安裝相依套件

```bash
# 安裝全域依賴
pip install -r requirements.txt

# 安裝各工具的依賴
pip install -r podcast-to-doc/requirements.txt
pip install -r hour_of_ai-image-generator/requirements.txt
```

### 2. 設定 API Key

複製 `.env.example` 為 `.env` 並填入你的 Gemini API Key：

```bash
GEMINI_API_KEY=your_api_key_here
```

### 3. 使用工具

**Podcast to Doc (YouTube 財經摘要):**
```bash
python podcast-to-doc/youtube_gemini_summary.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Hour of AI Image Generator (圖片生成):**
```bash
python hour_of_ai-image-generator/image_generator.py
```

## 🛠️ 工具列表

| 工具名稱 | 功能 | 模型 |
|---------|------|------|
| podcast-to-doc | YouTube 財經音訊摘要 | gemini-2.0-flash-lite |
| hour_of_ai-image-generator | 文字生成圖片 | gemini-2.0-flash-exp-image-generation |

## 📝 注意事項

- 請確保你有足夠的 Gemini API 配額
- 各工具的詳細使用方式請參考各自資料夾中的 README.md
- 所有工具共用專案根目錄的 `.env` 檔案

## 📄 License

個人使用，僅供參考學習。
