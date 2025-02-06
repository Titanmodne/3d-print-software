import tkinter as tk
from tkinter import filedialog, messagebox
import re


def process_gcode(input_file, output_file, x_offset, y_offset, z_offset):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # 记录处理过的输出行
    output_lines = []
    found_type = False  # 标志是否已经遇到;TYPE:标签
    current_type = None  # 当前文本块类型

    for i, line in enumerate(lines):
        line = line.strip()

        # 每当遇到空行时，添加 G92 E0 和 G92 J0
        if not line:  # 空行
            output_lines.append("")  # 保持空行
            continue  # 继续处理下一个行

        # 如果遇到;TYPE:标签，开始新的文本块
        if line.startswith(';TYPE:'):
            found_type = True
            current_type = line  # 当前文本块的类型
            output_lines.append(line)
            continue  # 保留;TYPE:标签并继续

        if found_type:
            # 只修改每个文本块的第一条 G1 或 G0 命令
            if (line.startswith('G1') or line.startswith('G0')) and output_lines[-1].startswith(';TYPE:'):
                # 复制当前命令并进行修改
                new_line = line
                # 修改 G1 或 G0 命令
                if 'X' in new_line:
                    new_line = re.sub(r'X(-?\d+(\.\d+)?)', lambda m: f"X{float(m.group(1)) + x_offset:.2f}", new_line)
                if 'Y' in new_line:
                    new_line = re.sub(r'Y(-?\d+(\.\d+)?)', lambda m: f"Y{float(m.group(1)) + y_offset:.2f}", new_line)
                if 'Z' in new_line:
                    new_line = re.sub(r'Z(-?\d+(\.\d+)?)', lambda m: f"Z{float(m.group(1)) + z_offset:.2f}", new_line)
                output_lines.append(new_line)  # 添加修改后的指令

                # 继续添加原始命令
                output_lines.append(line)
                found_type = False  # 处理完一条命令后重置标志
            else:
                # 其他命令直接添加，不做修改
                output_lines.append(line)
        else:
            # 在遇到;TYPE:之前的行直接添加
            output_lines.append(line)

    # 将结果写入输出文件
    with open(output_file, 'w') as outfile:
        outfile.write("\n".join(output_lines))


def select_input_file():
    input_path.set(filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")]))


def select_output_file():
    output_path.set(filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")]))


def process_files():
    input_file = input_path.get()
    output_file = output_path.get()
    x_offset = float(x_offset_entry.get())
    y_offset = float(y_offset_entry.get())
    z_offset = float(z_offset_entry.get())

    if not input_file or not output_file:
        messagebox.showerror("Error", "Please select both input and output files.")
        return

    try:
        process_gcode(input_file, output_file, x_offset, y_offset, z_offset)
        messagebox.showinfo("Success", "G-code processing completed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# 创建主窗口
root = tk.Tk()
root.title("G-code Processor")

# 输入文件路径变量
input_path = tk.StringVar()
output_path = tk.StringVar()

# 创建控件
input_label = tk.Label(root, text="Input File:")
input_label.pack(padx=10, pady=5)

input_button = tk.Button(root, text="Select Input File", command=select_input_file)
input_button.pack(padx=10, pady=5)

input_entry = tk.Entry(root, textvariable=input_path, width=40)
input_entry.pack(padx=10, pady=5)

output_label = tk.Label(root, text="Output File:")
output_label.pack(padx=10, pady=5)

output_button = tk.Button(root, text="Select Output File", command=select_output_file)
output_button.pack(padx=10, pady=5)

output_entry = tk.Entry(root, textvariable=output_path, width=40)
output_entry.pack(padx=10, pady=5)

# 添加输入框，允许用户设置XYZ偏移
x_offset_label = tk.Label(root, text="X Offset:")
x_offset_label.pack(padx=10, pady=5)

x_offset_entry = tk.Entry(root, width=20)
x_offset_entry.pack(padx=10, pady=5)
x_offset_entry.insert(0, "0.0")  # 默认值

y_offset_label = tk.Label(root, text="Y Offset:")
y_offset_label.pack(padx=10, pady=5)

y_offset_entry = tk.Entry(root, width=20)
y_offset_entry.pack(padx=10, pady=5)
y_offset_entry.insert(0, "0.0")  # 默认值

z_offset_label = tk.Label(root, text="Z Offset:")
z_offset_label.pack(padx=10, pady=5)

z_offset_entry = tk.Entry(root, width=20)
z_offset_entry.pack(padx=10, pady=5)
z_offset_entry.insert(0, "0.1")  # 默认值

process_button = tk.Button(root, text="Process Files", command=process_files)
process_button.pack(padx=10, pady=20)

# 运行GUI应用
root.mainloop()
