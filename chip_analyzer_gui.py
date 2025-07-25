#!/usr/bin/env python3
"""
晶片Pad與Pin分析器 - 圖形化界面
提供用戶友好的界面來分析晶片圖像
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from chip_pad_pin_analyzer import ChipPadPinAnalyzer
import json

class ChipAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("晶片Pad與Pin對應關係分析器")
        self.root.geometry("800x600")
        
        self.analyzer = ChipPadPinAnalyzer()
        self.input_file = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 標題
        title_label = ttk.Label(main_frame, text="晶片Pad與Pin對應關係分析器", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件選擇區域
        file_frame = ttk.LabelFrame(main_frame, text="圖像文件選擇", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        file_entry.grid(row=0, column=0, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="瀏覽", command=self.browse_file)
        browse_btn.grid(row=0, column=1)
        
        # 分析參數區域
        params_frame = ttk.LabelFrame(main_frame, text="分析參數", padding="10")
        params_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 預期pad數量
        ttk.Label(params_frame, text="預期Pad數量:").grid(row=0, column=0, sticky=tk.W)
        self.pad_count_var = tk.StringVar(value="152")
        pad_entry = ttk.Entry(params_frame, textvariable=self.pad_count_var, width=10)
        pad_entry.grid(row=0, column=1, padx=(5, 20))
        
        # 預期pin數量
        ttk.Label(params_frame, text="預期Pin數量:").grid(row=0, column=2, sticky=tk.W)
        self.pin_count_var = tk.StringVar(value="128")
        pin_entry = ttk.Entry(params_frame, textvariable=self.pin_count_var, width=10)
        pin_entry.grid(row=0, column=3, padx=(5, 0))
        
        # 控制按鈕
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        self.analyze_btn = ttk.Button(control_frame, text="開始分析", 
                                     command=self.start_analysis, style="Accent.TButton")
        self.analyze_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_btn = ttk.Button(control_frame, text="清除結果", command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_btn = ttk.Button(control_frame, text="導出結果", command=self.export_results)
        self.export_btn.pack(side=tk.LEFT)
        
        # 進度條
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 結果顯示區域
        results_frame = ttk.LabelFrame(main_frame, text="分析結果", padding="10")
        results_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 結果文本區域
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, width=80)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        file_frame.columnconfigure(0, weight=1)
    
    def browse_file(self):
        """瀏覽並選擇圖像文件"""
        file_types = [
            ("圖像文件", "*.jpg *.jpeg *.png *.bmp *.tiff"),
            ("所有文件", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="選擇晶片圖像文件",
            filetypes=file_types
        )
        
        if filename:
            self.file_path_var.set(filename)
            self.input_file = filename
            self.log_message(f"已選擇文件: {filename}")
    
    def start_analysis(self):
        """開始分析"""
        if not self.input_file:
            messagebox.showerror("錯誤", "請先選擇圖像文件")
            return
        
        if not os.path.exists(self.input_file):
            messagebox.showerror("錯誤", "選擇的文件不存在")
            return
        
        # 在後台線程中運行分析
        self.analyze_btn.config(state="disabled")
        self.progress.start()
        
        analysis_thread = threading.Thread(target=self.run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def run_analysis(self):
        """在後台執行分析"""
        try:
            self.log_message("=== 開始分析 ===")
            
            # 載入圖像
            self.log_message("載入圖像...")
            if not self.analyzer.load_image(self.input_file):
                self.log_message("ERROR: 無法載入圖像")
                return
            
            # 檢測pad
            self.log_message("檢測綠色pad...")
            pads = self.analyzer.detect_green_pads()
            self.log_message(f"檢測到 {len(pads)} 個pad")
            
            # 檢測pin
            self.log_message("檢測pin...")
            pins = self.analyzer.detect_pins()
            self.log_message(f"檢測到 {len(pins)} 個pin")
            
            # 檢測連接
            self.log_message("分析連接關係...")
            connections = self.analyzer.detect_connections()
            self.log_message(f"檢測到 {len(connections)} 個連接關係")
            
            # 生成視覺化結果
            self.log_message("生成視覺化結果...")
            output_image = "analysis_result.jpg"
            self.analyzer.visualize_results(output_image)
            
            # 導出映射表
            self.log_message("導出映射表...")
            mapping_data = self.analyzer.export_mapping_table()
            
            # 顯示總結
            self.show_analysis_summary(len(pads), len(pins), len(connections))
            
            self.log_message("=== 分析完成 ===")
            
        except Exception as e:
            self.log_message(f"ERROR: 分析過程中發生錯誤: {e}")
        finally:
            # 更新UI（在主線程中）
            self.root.after(0, self.analysis_completed)
    
    def analysis_completed(self):
        """分析完成後的UI更新"""
        self.progress.stop()
        self.analyze_btn.config(state="normal")
    
    def show_analysis_summary(self, pad_count, pin_count, connection_count):
        """顯示分析總結"""
        summary = f"""
=== 分析總結 ===
檢測到的Pad數量: {pad_count} (預期: {self.pad_count_var.get()})
檢測到的Pin數量: {pin_count} (預期: {self.pin_count_var.get()})
檢測到的連接關係: {connection_count}

分析完成度: {(connection_count / min(pad_count, pin_count) * 100):.1f}%

生成的文件:
- analysis_result.jpg (視覺化結果)
- pad_pin_mapping.json (映射表)
- vscode_mapping.json (VS Code擴展數據)
"""
        self.log_message(summary)
    
    def clear_results(self):
        """清除結果"""
        self.results_text.delete(1.0, tk.END)
        self.analyzer = ChipPadPinAnalyzer()  # 重置分析器
    
    def export_results(self):
        """導出結果到指定目錄"""
        if not hasattr(self.analyzer, 'connections') or not self.analyzer.connections:
            messagebox.showwarning("警告", "沒有分析結果可導出，請先執行分析")
            return
        
        output_dir = filedialog.askdirectory(title="選擇導出目錄")
        if output_dir:
            try:
                # 導出映射表
                mapping_file = os.path.join(output_dir, "pad_pin_mapping.json")
                self.analyzer.export_mapping_table(mapping_file)
                
                # 導出VS Code數據
                vscode_file = os.path.join(output_dir, "vscode_mapping.json")
                self.analyzer.export_vscode_extension_data(vscode_file)
                
                # 複製視覺化結果
                import shutil
                if os.path.exists("analysis_result.jpg"):
                    result_file = os.path.join(output_dir, "analysis_result.jpg")
                    shutil.copy("analysis_result.jpg", result_file)
                
                messagebox.showinfo("成功", f"結果已導出到: {output_dir}")
                self.log_message(f"結果已導出到: {output_dir}")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"導出失敗: {e}")
    
    def log_message(self, message):
        """記錄消息到結果區域"""
        self.results_text.insert(tk.END, message + "\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    app = ChipAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()