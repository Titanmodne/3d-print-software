import tkinter as tk
from tkinter import filedialog

def remove_first_line_from_each_block(input_path, output_path):
    with open(input_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    skip_next = True  # 从删除第一个数据块的第一行开始
    for line in lines:
        if line.strip() == "":
            # 遇到空行，重置skip_next，准备删除下一个数据块的第一行
            skip_next = True
            new_lines.append(line)
        elif skip_next:
            # 跳过这一行，不添加到new_lines中
            skip_next = False
        else:
            # 正常添加当前行到new_lines
            new_lines.append(line)

    # 将处理后的数据写入新文件
    with open(output_path, 'w') as file:
        file.writelines(new_lines)

def select_file():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    file_path = filedialog.askopenfilename()  # 打开文件选择对话框
    if file_path:
        output_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                   filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if output_path:
            remove_first_line_from_each_block(file_path, output_path)
            print(f'Processed file saved as {output_path}')
        else:
            print("No output file selected.")
    else:
        print("No file selected.")

select_file()