import tkinter as tk
from tkinter import filedialog


def process_gcode(input_file, output_file):
    result = []
    lines = []

    # 读取输入文件的所有行
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    delete_next_line = False  # 标记是否需要删除下一行
    delete_next_two_lines = False  # 标记是否需要删除前后两行
    first_t0 = True  # 标记是否为第一个T0
    first_t1 = True  # 标记是否为第一个T1

    for idx, line in enumerate(lines):
        line = line.strip()

        # 检查 T0 和 T1，处理不同情况
        if line == "T0":
            if first_t0:
                result.append(line + "\n")  # 保留第一个T0
                first_t0 = False
            else:
                if idx - 1 >= 0:  # 删除前一行
                    result.pop()
                result.append(line + "\n")

        elif line == "T1":
            if first_t1:
                # 第一个T1需要删除前一行和后一行
                if idx - 1 >= 0:
                    result.pop()  # 删除前一行
                delete_next_line = True  # 删除下一行
                result.append(line + "\n")
                first_t1 = False
            else:
                if idx - 1 >= 0:
                    result.pop()  # 删除前一行
                result.append(line + "\n")

        else:
            # 处理其他情况，检查是否需要删除当前行
            if delete_next_line:
                delete_next_line = False  # 重置删除标记
                continue  # 跳过当前行

            if delete_next_two_lines:
                delete_next_two_lines = False  # 重置删除标记
                continue  # 跳过当前行

            # 将非T0/T1行加入结果
            result.append(line + "\n")

    # 写入处理后的内容到输出文件
    with open(output_file, 'w') as outfile:
        outfile.writelines(result)


def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    input_entry.delete(0, tk.END)
    input_entry.insert(0, file_path)


def select_output_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    output_entry.delete(0, tk.END)
    output_entry.insert(0, file_path)


def process_files():
    input_file = input_entry.get()
    output_file = output_entry.get()
    if input_file and output_file:
        process_gcode(input_file, output_file)
        status_label.config(text="Processing Complete!")


# 创建主窗口
root = tk.Tk()
root.title("GCODE Processing Tool")

# 输入文件路径
input_label = tk.Label(root, text="Select Input File:")
input_label.pack(pady=5)
input_entry = tk.Entry(root, width=50)
input_entry.pack(pady=5)
input_button = tk.Button(root, text="Browse", command=select_input_file)
input_button.pack(pady=5)

# 输出文件路径
output_label = tk.Label(root, text="Select Output File:")
output_label.pack(pady=5)
output_entry = tk.Entry(root, width=50)
output_entry.pack(pady=5)
output_button = tk.Button(root, text="Browse", command=select_output_file)
output_button.pack(pady=5)

# 处理按钮
process_button = tk.Button(root, text="Process GCODE", command=process_files)
process_button.pack(pady=20)

# 状态标签
status_label = tk.Label(root, text="", fg="green")
status_label.pack(pady=5)

# 启动主事件循环
root.mainloop()
