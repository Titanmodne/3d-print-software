import sys
import numpy as np
import re
import argparse
import os

def process_gcode_to_array(input_filepath, output_filepath):
    # 读取切片软件生成的 Gcode 文件
    with open(input_filepath, "r") as f:
        data = f.readlines()
    n = len(data)

    jt = 8279 / 100
    et = 12300 / 100

    # 定义一个初始 m 行，7 列的二维数组，m 表示 m 个点
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
    p = 0  # 第 p 个点

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

    # 保存结果到输出文件
    write_array_to_file(arr, output_filepath)

def write_array_to_file(arr, output_filename="array.txt"):
    np.savetxt(output_filename, arr, fmt='%f', delimiter="\t")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理 G-code 文件并生成数组")
    parser.add_argument('--input', required=True, help='输入 G-code 文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    args = parser.parse_args()

    # 检查输入文件是否存在
    if not os.path.exists(args.input):
        print(f"错误：输入文件 '{args.input}' 不存在")
        sys.exit(1)

    # 处理 G-code 文件并保存结果
    try:
        process_gcode_to_array(args.input, args.output)
        print(f"处理完成。结果已保存至 {args.output}")
    except Exception as e:
        print(f"处理过程中发生错误：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main()