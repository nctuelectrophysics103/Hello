# 晶片Pad與Pin對應關係分析器

## 概述

這是一個專為分析晶片圖像中pad與pin對應關係而設計的自動化工具。該工具可以：
- 自動檢測晶片圖像中152個綠色框框表示的pad
- 識別die外圍的128個pin
- 分析紅色和紫色線條表示的連接關係
- 生成詳細的映射表和視覺化結果

## 功能特點

### 🔍 自動檢測
- **Pad檢測**: 使用顏色分割技術檢測綠色框框標記的pad
- **Pin檢測**: 使用邊緣檢測和特徵點檢測識別die外圍的pin
- **連接分析**: 自動追蹤紅色和紫色連接線，建立對應關係

### 📊 多種輸出格式
- **視覺化結果**: 生成標註了所有檢測元素的圖像
- **JSON映射表**: 結構化的pad-pin對應關係數據
- **VS Code整合**: 直接在編輯器中查看和管理結果

### 🛠️ 多種使用方式
- **命令行工具**: 批次處理和自動化腳本
- **GUI界面**: 用戶友好的圖形化操作
- **VS Code擴展**: 直接在開發環境中使用

## 安裝要求

### Python依賴項
```bash
pip install -r requirements.txt
```

### VS Code擴展依賴
```bash
npm install
npm run compile
```

## 使用方法

### 1. 命令行方式

```bash
# 基本使用
python chip_pad_pin_analyzer.py --input your_chip_image.jpg

# 自定義輸出路徑
python chip_pad_pin_analyzer.py --input chip.jpg --output result.jpg --mapping mapping.json
```

#### 參數說明
- `--input, -i`: 輸入的晶片圖像文件路徑
- `--output, -o`: 輸出的視覺化結果圖像路徑 (預設: analysis_result.jpg)
- `--mapping, -m`: 映射表輸出路徑 (預設: pad_pin_mapping.json)

### 2. GUI界面方式

```bash
python chip_analyzer_gui.py
```

功能包括：
- 📁 圖像文件選擇
- ⚙️ 分析參數設定
- 🚀 一鍵分析執行
- 📈 實時進度顯示
- 📋 詳細結果報告
- 💾 結果導出功能

### 3. VS Code擴展方式

#### 安裝擴展
1. 將項目文件夾放在VS Code擴展目錄中
2. 編譯TypeScript代碼：
   ```bash
   npm run compile
   ```
3. 在VS Code中按F5啟動擴展

#### 使用步驟
1. **右鍵點擊圖像文件** → 選擇 "分析晶片Pad與Pin對應關係"
2. **使用命令面板** (Ctrl+Shift+P) → 搜索 "晶片分析器"
3. **查看結果** → 命令面板 → "查看分析結果"

## 輸出文件說明

### 1. 視覺化結果 (analysis_result.jpg)
- 綠色圓圈和標籤：檢測到的pad位置
- 藍色圓圈和標籤：檢測到的pin位置
- 紅色連接線：分析出的對應關係

### 2. 映射表 (pad_pin_mapping.json)
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

### 3. VS Code數據 (vscode_mapping.json)
```json
{
  "chip_info": {
    "total_pads": 152,
    "total_pins": 128,
    "detected_pads": 150,
    "detected_pins": 125,
    "detected_connections": 120
  },
  "mapping": [
    {
      "pad_id": 1,
      "pin_id": 1,
      "pad_position": [x, y],
      "pin_position": [x, y]
    },
    ...
  ]
}
```

## 分析算法說明

### Pad檢測算法
1. **顏色空間轉換**: 將圖像從BGR轉換到HSV色彩空間
2. **顏色分割**: 使用HSV閾值檢測綠色區域
3. **形態學操作**: 消除噪聲和小斑點
4. **輪廓檢測**: 找到綠色框框的輪廓
5. **中心點計算**: 計算每個輪廓的幾何中心作為pad位置

### Pin檢測算法
1. **灰度轉換**: 將圖像轉換為灰度圖
2. **邊緣檢測**: 使用Canny算法檢測邊緣
3. **特徵檢測**: 結合霍夫圓檢測和角點檢測
4. **邊界過濾**: 只保留圖像邊緣附近的檢測點
5. **數量限制**: 根據預期數量（128）進行篩選

### 連接關係分析
1. **多顏色檢測**: 同時檢測紅色和紫色連接線
2. **線條檢測**: 使用霍夫線變換檢測直線段
3. **最近鄰匹配**: 將線條端點與最近的pad/pin關聯
4. **關係建立**: 建立pad到pin的映射關係

## 技術參數調整

### 顏色檢測參數
```python
# 綠色HSV範圍 (可根據實際圖像調整)
lower_green = np.array([40, 50, 50])
upper_green = np.array([80, 255, 255])

# 紅色HSV範圍
lower_red1 = np.array([0, 50, 50])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 50, 50])
upper_red2 = np.array([180, 255, 255])
```

### 檢測參數
```python
# 最小輪廓面積 (過濾小斑點)
min_contour_area = 50

# 霍夫圓檢測參數
param1 = 50      # 邊緣檢測閾值
param2 = 30      # 圓心檢測閾值
minRadius = 5    # 最小半徑
maxRadius = 50   # 最大半徑

# 邊界檢測範圍 (圖像邊緣的百分比)
border_threshold = 0.1  # 10%
```

## 故障排除

### 常見問題

#### 1. 檢測數量不準確
**原因**: 圖像質量問題或參數設置不當
**解決方案**:
- 檢查圖像清晰度和對比度
- 調整顏色檢測的HSV範圍
- 修改最小輪廓面積閾值

#### 2. 連接關係錯誤
**原因**: 線條檢測參數或顏色範圍不匹配
**解決方案**:
- 確認連接線的顏色確實是紅色或紫色
- 調整霍夫線檢測的閾值參數
- 增加最近鄰匹配的距離閾值

#### 3. Python依賴項問題
**解決方案**:
```bash
# 升級pip
pip install --upgrade pip

# 重新安裝依賴項
pip install --force-reinstall -r requirements.txt

# 如果OpenCV有問題
pip uninstall opencv-python
pip install opencv-python==4.8.1.78
```

### 效能優化建議

1. **圖像預處理**: 
   - 適當縮放圖像大小以提高處理速度
   - 增強圖像對比度以改善檢測效果

2. **參數調整**:
   - 根據具體的晶片類型調整檢測參數
   - 使用較小的搜索範圍以提高精度

3. **批次處理**:
   - 對於大量圖像，考慮使用並行處理

## 擴展開發

### 添加新的檢測算法
```python
class CustomPadDetector:
    def detect(self, image):
        # 實現自定義檢測邏輯
        pass
```

### 整合其他工具
- 可以與PCB設計軟件API整合
- 支援其他圖像格式和來源
- 添加機器學習模型以提高檢測精度

## 版本歷史

- **v1.0.0**: 初始版本，支援基本的pad/pin檢測和映射
- 未來計劃：添加機器學習檢測、批次處理、更多輸出格式

## 許可證

此項目僅供學習和研究使用。

## 聯絡方式

如有問題或建議，請通過以下方式聯絡：
- 提交GitHub Issue
- 發送電子郵件至項目維護者
