import sys
import numpy as np
import re
import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog


def process_gcode_to_array(file_path):
    # 读取切片软件生成的Gcode文件
    with open(file_path, "r") as f:
        data = f.readlines()
    n = len(data)

    jt = 8279 / 100
    et = 12300 / 100

    # 定义一个初始m行，7列的二维数组，m表示m个点。
    m = sum(1 for line in data if "G1" in line)
    arr = np.zeros((m, 7))

    # 正则表达式提取数据
    pax = r"X([-]?\d+\.?\d*)"
    pay = r"Y([-]?\d+\.?\d*)"
    paz = r"Z([-]?\d+\.?\d*)"
    pae = r"E([-]?\d+\.?\d*)"
    paj = r"J([-]?\d+\.?\d*)"
    paf = r"F(\d+)"

    x_value = y_value = z_value = e_value = j_value = f_value = exp = jxp = 0
    p = 0  # 第p个点

    for i in range(n):
        line = data[i]
        if "G92" in line:
            e_value = j_value = 0

        if "G1" in line:
            x_value = float(re.search(pax, line).group(1)) if re.search(pax, line) else x_value
            y_value = float(re.search(pay, line).group(1)) if re.search(pay, line) else y_value
            z_value = float(re.search(paz, line).group(1)) if re.search(paz, line) else z_value
            e = re.search(pae, line)
            if e:
                ex = e_value
                e_value = float(e.group(1))
                exp += e_value - ex
            j = re.search(paj, line)
            if j:
                jx = j_value
                j_value = float(j.group(1))
                jxp += j_value - jx
            f_value = float(re.search(paf, line).group(1)) if re.search(paf, line) else f_value

            arr[p] = [x_value, y_value, z_value, int(exp * et), int(jxp * jt), f_value / 60, 0]
            p += 1

        if "M280 P0 S95" in line:
            arr[p - 1, 6] = 3
        if "M280 P0 S2" in line:
            arr[p - 1, 6] = 1
        if "cut" in line:
            arr[p - 1, 6] = 2

    return arr


def write_array_to_file(arr, output_filename="array.txt"):
    np.savetxt(output_filename, arr, fmt='%f', delimiter="\t")


def select_input_file():
    file_path = filedialog.askopenfilename(title="Select Gcode File", filetypes=[("Gcode Files", "*.gcode;*.txt")])
    return file_path


def select_output_file():
    file_path = filedialog.asksaveasfilename(title="Save Processed File", defaultextension=".txt",
                                             filetypes=[("Text Files", "*.txt")])
    return file_path


if __name__ == "__main__":
    # 创建Tkinter根窗口并隐藏
    root = tk.Tk()
    root.withdraw()

    # 选择输入文件
    gcode_file = select_input_file()
    if not gcode_file:
        print("No input file selected. Exiting.")
        sys.exit(1)

    # 选择输出文件
    output_file = select_output_file()
    if not output_file:
        print("No output file selected. Exiting.")
        sys.exit(1)

    # 处理G-code文件并保存结果
    result_array = process_gcode_to_array(gcode_file)
    write_array_to_file(result_array, output_file)

    print(f"Processing complete. Results saved to {output_file}")
