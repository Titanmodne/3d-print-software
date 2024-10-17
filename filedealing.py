import tkinter as tk
from tkinter import filedialog
import re

def convert_gcode_format(input_file_path, output_file_path):
    try:
        with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
            for line in infile:
                # 匹配并解析原始格式中的数据
                match = re.search(r'G1 - X: ([\d\.-]+), Y: ([\d\.-]+), Z: ([\d\.-]+) J: ([\d\.-]+) F: (\d+\.?\d*)', line)
                if match:
                    x, y, z, j, f = match.groups()
                    # 转换为新的格式并写入文件
                    new_line = f'G1 X{x} Y{y} Z{z} J{j} F{f}\n'
                    outfile.write(new_line)
                else:
                    # 如果不匹配，原样写入
                    outfile.write(line)
        print(f"文件已转换并保存到 {output_file_path}")
    except Exception as e:
        print(f"处理文件时出错: {e}")

def select_files_and_convert():
    """选择文件并执行格式转换"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    input_file_path = filedialog.askopenfilename(title="选择原始格式的G-code文件", filetypes=[("Text files", "*.txt"), ("G-code files", "*.gcode")])
    if not input_file_path:
        print("未选择输入文件")
        return

    output_file_path = filedialog.asksaveasfilename(defaultextension=".txt", title="保存转换后的G-code文件", filetypes=[("Text files", "*.txt"), ("G-code files", "*.gcode")])
    if not output_file_path:
        print("未选择保存文件")
        return

    convert_gcode_format(input_file_path, output_file_path)

if __name__ == "__main__":
    select_files_and_convert()
