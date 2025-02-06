import tkinter as tk
from tkinter import filedialog

def add_commands_and_swap_T0_T1(file_path, output_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # 在文件开头添加 M211 S0
    lines.insert(0, "M211 S0\n")

    # 创建一个新的列表来存储修改后的行
    new_lines = []

    for line in lines:
        # 如果是T0，在T0前面添加M400和M280 P0 S95
        if 'T0' in line:
            new_lines.append("M400\n")
            new_lines.append("M280 P0 S95\n")
            new_lines.append("M400\n")
            new_lines.append(line.replace('T0', 'TEMP').replace('T1', 'T0').replace('TEMP', 'T1'))
        # 如果是T1，在T1前面添加M400和M280 P0 S2
        elif 'T1' in line:
            new_lines.append("M400\n")
            new_lines.append("M280 P0 S2\n")
            new_lines.append("M400\n")
            new_lines.append(line.replace('T1', 'TEMP').replace('T0', 'T1').replace('TEMP', 'T0'))
        # 如果是;TYPE:语句，在其前面添加G92 E0和G92 J0
        elif ';TYPE:' in line:
            new_lines.append("G92 E0\n")  # 添加G92 E0
            new_lines.append("G92 J0\n")  # 添加G92 J0
            new_lines.append(line)
        else:
            new_lines.append(line)

    # 将修改后的内容写入到输出文件
    with open(output_path, 'w') as file:
        file.writelines(new_lines)

def select_file():
    file_path = filedialog.askopenfilename(title="选择输入文件", filetypes=[("Text files", "*.txt")])
    if file_path:
        output_path = filedialog.asksaveasfilename(title="选择保存文件", defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if output_path:
            add_commands_and_swap_T0_T1(file_path, output_path)
            print("文件处理完成，已保存至:", output_path)

# 创建Tkinter界面
root = tk.Tk()
root.withdraw()  # 隐藏主窗口
select_file()
