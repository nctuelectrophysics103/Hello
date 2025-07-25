# 晶片Pad與Pin分析器 - 快速開始指南

## 🚀 快速開始

### 第一步：激活虛擬環境
```bash
source chip_analyzer_env/bin/activate
```

### 第二步：使用方式

#### 🖥️ 方式1：圖形化界面（推薦新手）
```bash
python3 chip_analyzer_gui.py
```
- 點擊「瀏覽」選擇您的晶片圖像
- 設定預期的pad數量（152）和pin數量（128）
- 點擊「開始分析」
- 等待分析完成，查看結果

#### 💻 方式2：命令行（推薦批次處理）
```bash
# 基本使用
python3 chip_pad_pin_analyzer.py --input your_chip_image.jpg

# 完整參數示例
python3 chip_pad_pin_analyzer.py --input chip.jpg --output result.jpg --mapping mapping.json
```

#### 🔧 方式3：VS Code擴展
1. 在VS Code中右鍵點擊圖像文件
2. 選擇「分析晶片Pad與Pin對應關係」
3. 或使用命令面板（Ctrl+Shift+P）搜索「晶片分析器」

## 📁 輸出文件說明

分析完成後，您將得到以下文件：

### 1. `analysis_result.jpg` - 視覺化結果
- 綠色圓圈：檢測到的pad位置及編號
- 藍色圓圈：檢測到的pin位置及編號  
- 紅色線條：分析出的連接關係

### 2. `pad_pin_mapping.json` - 詳細映射表
```json
{
  "total_pads": 152,
  "total_pins": 128,
  "connections": {
    "PAD_1": "PIN_1",
    "PAD_2": "PIN_15",
    ...
  },
  "pad_positions": [[x1, y1], [x2, y2], ...],
  "pin_positions": [[x1, y1], [x2, y2], ...]
}
```

### 3. `vscode_mapping.json` - VS Code格式數據
適用於進一步處理或集成到其他工具中的結構化數據。

## ⚙️ 重要參數調整

如果檢測效果不理想，您可以調整以下參數：

### 顏色檢測範圍（在 `chip_pad_pin_analyzer.py` 中）：
```python
# 綠色HSV範圍（用於pad檢測）
lower_green = np.array([40, 50, 50])    # 可調整為 [35, 40, 40]
upper_green = np.array([80, 255, 255])  # 可調整為 [85, 255, 255]

# 紅色HSV範圍（用於連接線檢測）
lower_red1 = np.array([0, 50, 50])
upper_red1 = np.array([10, 255, 255])
```

### 檢測靈敏度調整：
```python
# 最小輪廓面積（過濾小噪點）
min_contour_area = 50  # 增大此值過濾更多噪點

# 邊界檢測範圍
border_threshold = 0.1  # 0.05-0.2 之間調整
```

## 🛠️ 故障排除

### 問題1：檢測到的pad/pin數量不準確
**解決方案**：
1. 檢查圖像質量，確保清晰度足夠
2. 調整顏色檢測的HSV範圍
3. 修改最小輪廓面積閾值

### 問題2：連接關係錯誤
**解決方案**：
1. 確認連接線顏色是否為純紅色或紫色
2. 增加線條檢測的閾值參數
3. 檢查圖像中是否有干擾線條

### 問題3：程式運行錯誤
**解決方案**：
```bash
# 重新激活虛擬環境
source chip_analyzer_env/bin/activate

# 檢查依賴項
python3 -c "import cv2, numpy, matplotlib; print('依賴項正常')"

# 重新安裝依賴項（如果需要）
pip install --force-reinstall -r requirements.txt
```

## 💡 使用技巧

1. **圖像品質**：使用高解析度、對比度良好的圖像
2. **顏色標準化**：確保pad用純綠色標記，連接線用純紅色或紫色
3. **批次處理**：對於多張圖像，使用命令行方式並編寫腳本
4. **結果驗證**：始終檢查視覺化結果以確認分析準確性

## 📞 需要幫助？

如果遇到問題，請檢查：
1. 圖像格式是否支援（JPG, PNG, BMP, TIFF）
2. 虛擬環境是否正確激活
3. 所有依賴項是否正確安裝
4. 圖像中的標記顏色是否符合預期

祝您使用愉快！🎉