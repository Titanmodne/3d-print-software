import re
import math
import tkinter as tk
from tkinter import filedialog, simpledialog


# 提取坐标的函数
def extract_coordinates(input_file):
    coordinates = []
    original_lines = []
    with open(input_file, 'r') as file:
        for line in file:
            original_line = line.strip()
            original_lines.append(original_line)  # 保留原始行
            if original_line:
                parts = re.findall(r'X([+-]?\d*\.?\d+)\s*Y([+-]?\d*\.?\d+)\s*Z([+-]?\d*\.?\d+)', original_line)
                if parts:
                    x, y, z = map(float, parts[0])
                    coordinates.append((x, y, z))
                else:
                    coordinates.append(None)  # 保存无坐标行为None
            else:
                coordinates.append(None)  # 保存空行为None
    return coordinates, original_lines


# 计算坐标距离并根据T0和T1选择不同的计算方式
def calculate_distances(coordinates, original_lines, k1, k2, f):
    output_lines = []
    accumulated_e = 0  # T0后的累积E值
    accumulated_j = 0  # T1后的累积J值
    previous_coordinate = None
    use_e = True  # 默认使用E值计算（从T0开始）

    for i, coordinate in enumerate(coordinates):
        line = original_lines[i]

        # 检测T0和T1命令，并更新使用的计算方式
        if 'T0' in line:
            use_e = True  # T0之后使用E值
            accumulated_j = 0  # 切换到T0时重置J
            output_lines.append(line)  # 保留T0的行
            continue
        elif 'T1' in line:
            use_e = False  # T1之后使用J值
            accumulated_e = 0  # 切换到T1时重置E
            output_lines.append(line)  # 保留T1的行
            continue

        # 对其他行进行坐标计算处理
        if coordinate is None:
            output_lines.append(line)  # 保留无坐标的原始行
            accumulated_e = 0  # 检测到无坐标行为时重置E值
            accumulated_j = 0  # 检测到无坐标行为时重置J值
            previous_coordinate = None  # 清除上一坐标
            continue

        # 提取坐标并计算距离
        x, y, z = coordinate
        if previous_coordinate:
            x1, y1, z1 = previous_coordinate
            distance = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)

            if use_e:
                e = distance * k1
                accumulated_e += e
                modified_line = f"{line} E{accumulated_e:.5f} F{f}"
            else:
                j = distance * k2
                accumulated_j += j
                modified_line = f"{line} J{accumulated_j:.2f} F{f}"
        else:
            # 对第一条数据直接设置E值为0.00或J值为0.00，F值由输入指定
            if use_e:
                modified_line = f"{line} E0.00000 F{f}"
            else:
                modified_line = f"{line} J0.00 F{f}"

        output_lines.append(modified_line)
        previous_coordinate = (x, y, z)

    return output_lines


# 选择输入输出文件并输入K1, K2, F的值
def choose_files_and_process():
    # 创建Tkinter窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 选择输入文件
    input_file_path = filedialog.askopenfilename(title="选择输入文件",
                                                 filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if not input_file_path:
        print("未选择输入文件.")
        return

    # 选择输出文件
    output_file_path = filedialog.asksaveasfilename(title="选择输出文件", defaultextension=".txt",
                                                    filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if not output_file_path:
        print("未选择输出文件.")
        return

    # 输入K1, K2, F的值
    k1 = simpledialog.askfloat("输入K1", "请输入K1的值：", minvalue=0.0)
    k2 = simpledialog.askfloat("输入K2", "请输入K2的值：", minvalue=0.0)
    f = simpledialog.askfloat("输入F", "请输入F的值：", minvalue=0.0)

    # 处理文件
    process_jcount(input_file_path, output_file_path, k1, k2, f)


# 处理主程序
def process_jcount(input_file_path, output_file_path, k1, k2, f):
    coordinates, original_lines = extract_coordinates(input_file_path)
    if not coordinates:
        print("未提取到坐标数据.")
        return

    output_lines = calculate_distances(coordinates, original_lines, k1, k2, f)

    with open(output_file_path, 'w') as file:
        for line in output_lines:
            file.write(line + "\n")

    print(f"处理后的数据已保存到 {output_file_path}")


# 运行程序
choose_files_and_process()
