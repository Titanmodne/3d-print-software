import re
import tkinter as tk
from tkinter import filedialog

def process_file(input_text):
    # 按行处理输入文本
    lines = input_text.splitlines()
    result_lines = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 处理G0/G1指令的块
        if line.startswith(('G0', 'G1')):
            # 获取当前行和下一行的Z值进行比较
            if i + 1 < len(lines):  # 确保有第二行
                match1 = re.search(r'Z([+-]?[0-9]*\.?[0-9]+)', lines[i])
                match2 = re.search(r'Z([+-]?[0-9]*\.?[0-9]+)', lines[i + 1])

                if match1 and match2:
                    z1 = float(match1.group(1))
                    z2 = float(match2.group(1))

                    # 如果当前行的 Z 值大于下一行的 Z 值，则删除当前行
                    if z1 > z2:
                        i += 1  # 跳过当前行
                        continue  # 跳过当前行并处理下一行

            # 将有效行加入结果
            result_lines.append(line)

            # 检查是否下一行不是G0/G1指令，如果是，则添加一个空行
            if i + 1 < len(lines) and not lines[i + 1].startswith(('G0', 'G1')):
                result_lines.append("")  # 添加空行

        else:
            result_lines.append(line)

        i += 1

    # 返回处理后的文本
    return '\n'.join(result_lines)


def select_file():
    # 打开文件选择对话框并返回文件路径
    file_path = filedialog.askopenfilename(title="选择输入文件", filetypes=[("Text Files", "*.txt")])
    return file_path


def save_file(content):
    # 打开文件保存对话框并保存内容到指定文件
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if save_path:
        with open(save_path, 'w') as file:
            file.write(content)


def main():
    # 创建 Tkinter 主窗口并隐藏
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 选择输入文件
    input_file = select_file()
    if not input_file:
        print("未选择输入文件")
        return

    # 读取输入文件
    with open(input_file, 'r') as file:
        input_text = file.read()

    # 处理数据
    output_text = process_file(input_text)

    # 选择输出文件并保存结果
    save_file(output_text)
    print("处理完成，结果已保存。")


if __name__ == "__main__":
    main()
