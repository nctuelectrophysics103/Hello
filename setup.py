#!/usr/bin/env python3
"""
晶片Pad與Pin分析器 - 安裝和設置腳本
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """檢查Python版本"""
    if sys.version_info < (3, 7):
        print("錯誤: 需要Python 3.7或更高版本")
        sys.exit(1)
    print(f"✓ Python版本: {sys.version}")

def install_dependencies():
    """安裝Python依賴項"""
    print("正在安裝Python依賴項...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Python依賴項安裝完成")
    except subprocess.CalledProcessError as e:
        print(f"錯誤: 無法安裝依賴項 - {e}")
        sys.exit(1)

def test_opencv():
    """測試OpenCV安裝"""
    try:
        import cv2
        print(f"✓ OpenCV版本: {cv2.__version__}")
    except ImportError:
        print("警告: OpenCV未正確安裝")
        return False
    return True

def test_imports():
    """測試所有重要的import"""
    modules = ['numpy', 'matplotlib', 'PIL', 'cv2']
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} 可用")
        except ImportError:
            print(f"✗ {module} 不可用")
            return False
    return True

def create_example_script():
    """創建示例使用腳本"""
    example_script = """#!/usr/bin/env python3
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
"""
    
    with open("example_usage.py", "w", encoding="utf-8") as f:
        f.write(example_script)
    print("✓ 示例腳本已創建: example_usage.py")

def setup_vscode_extension():
    """設置VS Code擴展"""
    if os.path.exists("package.json"):
        print("正在設置VS Code擴展...")
        try:
            # 檢查是否有npm
            subprocess.check_call(["npm", "--version"], 
                                 stdout=subprocess.DEVNULL, 
                                 stderr=subprocess.DEVNULL)
            
            # 安裝依賴項
            subprocess.check_call(["npm", "install"])
            
            # 編譯TypeScript
            subprocess.check_call(["npm", "run", "compile"])
            
            print("✓ VS Code擴展設置完成")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("警告: npm不可用，跳過VS Code擴展設置")
            return False
    return True

def main():
    """主設置函數"""
    print("晶片Pad與Pin分析器 - 安裝程序")
    print("=" * 40)
    
    # 檢查Python版本
    check_python_version()
    
    # 安裝依賴項
    install_dependencies()
    
    # 測試導入
    if not test_imports():
        print("警告: 某些模組無法導入，可能會影響功能")
    
    # 測試OpenCV
    test_opencv()
    
    # 創建示例腳本
    create_example_script()
    
    # 設置VS Code擴展
    setup_vscode_extension()
    
    print("\n" + "=" * 40)
    print("安裝完成！")
    print("\n使用方法:")
    print("1. 命令行: python chip_pad_pin_analyzer.py --input your_image.jpg")
    print("2. GUI界面: python chip_analyzer_gui.py")
    print("3. 示例: python example_usage.py your_image.jpg")
    print("4. VS Code: 安裝擴展後右鍵點擊圖像文件")

if __name__ == "__main__":
    main()