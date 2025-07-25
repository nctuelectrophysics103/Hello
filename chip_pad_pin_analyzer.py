#!/usr/bin/env python3
"""
晶片Pad與Pin對應關係分析器
自動識別晶片圖像中的pad和pin，並分析它們之間的連接關係
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import json
import os
from typing import Dict, List, Tuple, Optional
import argparse

class ChipPadPinAnalyzer:
    def __init__(self):
        self.pad_positions = []  # 152個pad的位置
        self.pin_positions = []  # 128個pin的位置
        self.connections = {}    # pad到pin的映射關係
        self.image = None
        self.processed_image = None
        
    def load_image(self, image_path: str) -> bool:
        """載入晶片圖像"""
        try:
            self.image = cv2.imread(image_path)
            if self.image is None:
                print(f"無法載入圖像: {image_path}")
                return False
            print(f"成功載入圖像: {image_path}")
            print(f"圖像尺寸: {self.image.shape}")
            return True
        except Exception as e:
            print(f"載入圖像時發生錯誤: {e}")
            return False
    
    def detect_green_pads(self) -> List[Tuple[int, int]]:
        """檢測綠色框框表示的pad"""
        if self.image is None:
            return []
        
        # 轉換到HSV顏色空間
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 定義綠色的HSV範圍
        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        
        # 創建綠色遮罩
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # 形態學操作來清理遮罩
        kernel = np.ones((3, 3), np.uint8)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
        green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
        
        # 尋找輪廓
        contours, _ = cv2.findContours(green_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        pads = []
        for contour in contours:
            # 過濾太小的輪廓
            if cv2.contourArea(contour) > 50:
                # 計算輪廓的中心點
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    pads.append((cx, cy))
        
        self.pad_positions = pads
        print(f"檢測到 {len(pads)} 個綠色pad")
        return pads
    
    def detect_pins(self) -> List[Tuple[int, int]]:
        """檢測die外圍的pin"""
        if self.image is None:
            return []
        
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # 邊緣檢測
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # 霍夫圓檢測（假設pin是圓形或接近圓形）
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                 param1=50, param2=30, minRadius=5, maxRadius=50)
        
        pins = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            
            # 過濾邊緣附近的圓形（pin通常在die外圍）
            height, width = gray.shape
            border_threshold = min(width, height) * 0.1  # 邊界閾值
            
            for (x, y, r) in circles:
                # 檢查是否在邊緣附近
                if (x < border_threshold or x > width - border_threshold or
                    y < border_threshold or y > height - border_threshold):
                    pins.append((x, y))
        
        # 如果霍夫圓檢測效果不好，使用角點檢測作為備選
        if len(pins) < 100:
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=200, qualityLevel=0.01, minDistance=10)
            if corners is not None:
                for corner in corners:
                    x, y = corner.ravel()
                    x, y = int(x), int(y)
                    # 檢查是否在邊緣附近
                    height, width = gray.shape
                    border_threshold = min(width, height) * 0.15
                    if (x < border_threshold or x > width - border_threshold or
                        y < border_threshold or y > height - border_threshold):
                        pins.append((x, y))
        
        self.pin_positions = pins[:128]  # 限制為128個pin
        print(f"檢測到 {len(self.pin_positions)} 個pin")
        return self.pin_positions
    
    def detect_connections(self) -> Dict[int, int]:
        """檢測紅色和紫色線條連接關係"""
        if self.image is None or not self.pad_positions or not self.pin_positions:
            return {}
        
        # 轉換到HSV顏色空間
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        
        # 定義紅色的HSV範圍
        lower_red1 = np.array([0, 50, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 50, 50])
        upper_red2 = np.array([180, 255, 255])
        
        # 定義紫色的HSV範圍
        lower_purple = np.array([120, 50, 50])
        upper_purple = np.array([150, 255, 255])
        
        # 創建顏色遮罩
        red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        purple_mask = cv2.inRange(hsv, lower_purple, upper_purple)
        
        # 合併遮罩
        connection_mask = cv2.bitwise_or(red_mask1, red_mask2)
        connection_mask = cv2.bitwise_or(connection_mask, purple_mask)
        
        # 形態學操作
        kernel = np.ones((3, 3), np.uint8)
        connection_mask = cv2.morphologyEx(connection_mask, cv2.MORPH_CLOSE, kernel)
        
        # 尋找線條
        lines = cv2.HoughLinesP(connection_mask, 1, np.pi/180, threshold=20, 
                               minLineLength=30, maxLineGap=10)
        
        connections = {}
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                
                # 找到最近的pad和pin
                closest_pad_idx = self._find_closest_point((x1, y1), self.pad_positions)
                closest_pin_idx = self._find_closest_point((x2, y2), self.pin_positions)
                
                if closest_pad_idx is not None and closest_pin_idx is not None:
                    connections[closest_pad_idx] = closest_pin_idx
        
        self.connections = connections
        print(f"檢測到 {len(connections)} 個連接關係")
        return connections
    
    def _find_closest_point(self, point: Tuple[int, int], points_list: List[Tuple[int, int]], 
                           max_distance: float = 50.0) -> Optional[int]:
        """找到最近的點"""
        if not points_list:
            return None
        
        min_distance = float('inf')
        closest_idx = None
        
        for idx, (px, py) in enumerate(points_list):
            distance = np.sqrt((point[0] - px) ** 2 + (point[1] - py) ** 2)
            if distance < min_distance and distance <= max_distance:
                min_distance = distance
                closest_idx = idx
        
        return closest_idx
    
    def visualize_results(self, output_path: str = "analysis_result.jpg"):
        """視覺化分析結果"""
        if self.image is None:
            return
        
        result_image = self.image.copy()
        
        # 繪製pad（綠色圓圈）
        for idx, (x, y) in enumerate(self.pad_positions):
            cv2.circle(result_image, (x, y), 8, (0, 255, 0), 2)
            cv2.putText(result_image, f"P{idx+1}", (x-15, y-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # 繪製pin（藍色圓圈）
        for idx, (x, y) in enumerate(self.pin_positions):
            cv2.circle(result_image, (x, y), 6, (255, 0, 0), 2)
            cv2.putText(result_image, f"N{idx+1}", (x-15, y+25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
        
        # 繪製連接線
        for pad_idx, pin_idx in self.connections.items():
            if pad_idx < len(self.pad_positions) and pin_idx < len(self.pin_positions):
                pad_pos = self.pad_positions[pad_idx]
                pin_pos = self.pin_positions[pin_idx]
                cv2.line(result_image, pad_pos, pin_pos, (0, 0, 255), 2)
        
        cv2.imwrite(output_path, result_image)
        print(f"分析結果已保存到: {output_path}")
    
    def export_mapping_table(self, output_path: str = "pad_pin_mapping.json"):
        """導出pad到pin的映射表"""
        mapping_data = {
            "total_pads": len(self.pad_positions),
            "total_pins": len(self.pin_positions),
            "connections": {},
            "pad_positions": self.pad_positions,
            "pin_positions": self.pin_positions
        }
        
        # 轉換連接關係為更可讀的格式
        for pad_idx, pin_idx in self.connections.items():
            pad_name = f"PAD_{pad_idx + 1}"
            pin_name = f"PIN_{pin_idx + 1}"
            mapping_data["connections"][pad_name] = pin_name
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, indent=2, ensure_ascii=False)
        
        print(f"映射表已導出到: {output_path}")
        return mapping_data
    
    def export_vscode_extension_data(self, output_path: str = "vscode_mapping.json"):
        """為VS Code擴展導出格式化的數據"""
        vscode_data = {
            "chip_info": {
                "total_pads": 152,
                "total_pins": 128,
                "detected_pads": len(self.pad_positions),
                "detected_pins": len(self.pin_positions),
                "detected_connections": len(self.connections)
            },
            "mapping": []
        }
        
        for pad_idx, pin_idx in self.connections.items():
            vscode_data["mapping"].append({
                "pad_id": pad_idx + 1,
                "pin_id": pin_idx + 1,
                "pad_position": self.pad_positions[pad_idx] if pad_idx < len(self.pad_positions) else None,
                "pin_position": self.pin_positions[pin_idx] if pin_idx < len(self.pin_positions) else None
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(vscode_data, f, indent=2, ensure_ascii=False)
        
        print(f"VS Code擴展數據已導出到: {output_path}")
        return vscode_data

def main():
    parser = argparse.ArgumentParser(description='晶片Pad與Pin對應關係分析器')
    parser.add_argument('--input', '-i', required=True, help='輸入圖像文件路徑')
    parser.add_argument('--output', '-o', default='analysis_result.jpg', help='輸出圖像文件路徑')
    parser.add_argument('--mapping', '-m', default='pad_pin_mapping.json', help='映射表輸出路徑')
    
    args = parser.parse_args()
    
    # 創建分析器實例
    analyzer = ChipPadPinAnalyzer()
    
    # 載入圖像
    if not analyzer.load_image(args.input):
        return
    
    # 執行分析
    print("開始分析...")
    print("1. 檢測pad...")
    analyzer.detect_green_pads()
    
    print("2. 檢測pin...")
    analyzer.detect_pins()
    
    print("3. 分析連接關係...")
    analyzer.detect_connections()
    
    # 生成結果
    print("4. 生成視覺化結果...")
    analyzer.visualize_results(args.output)
    
    print("5. 導出映射表...")
    analyzer.export_mapping_table(args.mapping)
    
    print("6. 導出VS Code擴展數據...")
    analyzer.export_vscode_extension_data()
    
    print("分析完成！")

if __name__ == "__main__":
    main()