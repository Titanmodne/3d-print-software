import tkinter as tk
from tkinter import filedialog
import re


def process_gcode(input_file, output_file):
    # 初始化变量
    current_printhead = None
    last_x = 0.0
    last_y = 0.0
    last_z = 0.0
    result = []
    skip_next_lines = 0  # 用于跳过下一行数据
    prev_line = None  # 用于存储上一次的行
    prev_g0_line = None  # 用于存储上一次的G0行
    first_g1_line = True  # 用于标记是否是第一条G1指令
    skip_first_g1 = False  # 用于跳过第一条G1指令的标志

    with open(input_file, 'r') as infile:
        for line in infile:
            line = line.strip()

            # 检查是否为G91指令，如果是，停止提取
            if line.startswith("G91"):
                break  # 退出循环，停止处理

            # 如果要跳过这一行，直接跳过
            if skip_next_lines > 0:
                skip_next_lines -= 1
                continue

            # 保留所有含有;TYPE:或;LAYER:的行
            if ";TYPE:" in line or ";LAYER:" in line:
                if skip_first_g1:  # 如果已经跳过第一条G1，则将下一条G1指令合并到;TYPE:后
                    skip_first_g1 = False  # 重置标志
                    result.append(line + "\n")  # 添加当前;TYPE:行
                    continue
                else:
                    result.append(line + "\n")
                    continue

            # 严格检查T0和T1打印头，只有完全是T0或T1时才记录
            if line == "T0":
                current_printhead = "T0"
                result.append("T0\n")  # T0单独一行
                continue
            elif line == "T1":
                current_printhead = "T1"
                result.append("T1\n")  # T1单独一行
                continue

            # 检测G0或G1指令
            match = re.match(
                r'(G0|G1)\s*(F\d+)?\s*(X[-+]?[0-9]*\.?[0-9]+)?\s*(Y[-+]?[0-9]*\.?[0-9]+)?\s*(Z[-+]?[0-9]*\.?[0-9]+)?\s*(E[-+]?[0-9]*\.?[0-9]+)?',
                line)
            if match:
                g_code = match.group(1)
                x_value = match.group(3)
                y_value = match.group(4)
                z_value = match.group(5)

                # 更新X, Y, Z值
                if x_value:
                    last_x = round(float(x_value[1:]), 2)
                if y_value:
                    last_y = round(float(y_value[1:]), 2)
                if z_value:
                    last_z = round(float(z_value[1:]), 2)

                # 如果是第一条G1指令，跳过它并标记需要合并第二条G1指令
                if first_g1_line:
                    first_g1_line = False
                    skip_first_g1 = True
                    continue

                # 保留G0指令，并保留Z值
                if g_code == "G0":
                    output_line = f"{g_code} X{last_x} Y{last_y} Z{last_z}\n"
                    result.append(output_line)
                    continue  # 跳过当前G0行，直接进行下一次循环

                # 处理G1指令，并保存到结果
                if current_printhead == "T0" or current_printhead == "T1":
                    output_line = f"{g_code} X{last_x} Y{last_y} Z{last_z}\n"
                    result.append(output_line)

    # 写入结果到文件
    with open(output_file, 'w') as outfile:
        for line in result:
            outfile.write(line)


def select_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("GCODE Files", "*.gcode")])
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
input_label = tk.Label(root, text="Select GCODE Input File:")
input_label.pack(pady=5)
input_entry = tk.Entry(root, width=50)
input_entry.pack(pady=5)
input_button = tk.Button(root, text="Browse", command=select_input_file)
input_button.pack(pady=5)

# 输出文件路径
output_label = tk.Label(root, text="Select Output TXT File:")
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
