#!/usr/bin/env python3
# 示例使用腳本

from chip_pad_pin_analyzer import ChipPadPinAnalyzer
import sys

def main():
    if len(sys.argv) != 2:
        print("使用方法: python example_usage.py <image_path>")
        return
    
    image_path = sys.argv[1]
    analyzer = ChipPadPinAnalyzer()
    
    print(f"分析圖像: {image_path}")
    
    # 載入圖像
    if not analyzer.load_image(image_path):
        print("無法載入圖像")
        return
    
    # 執行分析
    analyzer.detect_green_pads()
    analyzer.detect_pins()
    analyzer.detect_connections()
    
    # 生成結果
    analyzer.visualize_results("example_result.jpg")
    analyzer.export_mapping_table("example_mapping.json")
    
    print("分析完成！結果已保存。")

if __name__ == "__main__":
    main()
