# Hour of AI - Image Generator

使用 Google Gemini 2.0 Flash 圖片生成模型來創建 AI 圖片的工具。

## 功能

- 輸入文字提示詞生成圖片
- 使用 Gemini 2.0 Flash Image Generation 模型
- 自動調整為 1:1 比例 (512x512)
- 圖片自動儲存到 `generated_images/` 資料夾

## 安裝

```bash
pip install -r requirements.txt
```

## 設定

複製 `.env.example` 到 `.env` 並填入你的 Gemini API Key：

```bash
GEMINI_API_KEY=your_api_key_here
```

## 使用方法

### 基本使用

```bash
python image_generator.py
```

程式會提示你輸入提示詞，然後生成圖片。

### 使用範例

```
請輸入圖片提示詞: 一隻可愛的貓咪坐在月球上，看著地球，卡通風格
```

圖片將儲存在 `generated_images/` 資料夾，檔名格式：`image_YYYYMMDD_HHMMSS.png`

## 模型資訊

- **模型**: `gemini-2.0-flash-exp-image-generation`
- **圖片尺寸**: 512x512 (1:1 比例)
- **輸出格式**: PNG

## 注意事項

- 請確保你有足夠的 Gemini API 配額
- 圖片生成可能需要幾秒鐘時間
- 生成的圖片僅供個人使用，請遵守 Google 的使用條款
