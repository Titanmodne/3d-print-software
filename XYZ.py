import re
import tkinter as tk
from tkinter import filedialog


def extract_coordinates(gcode_file):
    """
    提取G-code文件中的坐标，并处理Z值的缺失情况。
    如果之前没有有效的X、Y、Z值，则将其设置为0。
    """
    coordinates = []
    current_x = 0  # 当前的X值，初始为0
    current_y = 0  # 当前的Y值，初始为0
    current_z = 0  # 当前的Z值，初始为0

    # 改进后的正则表达式匹配所有可能的G0/G1指令
    gcode_pattern = re.compile(
        r'^(G[01])\s*(F[+-]?\d*\.?\d+)?\s*(X[+-]?\d*\.?\d+)?\s*(Y[+-]?\d*\.?\d+)?\s*(Z[+-]?\d*\.?\d+)?', re.MULTILINE)

    with open(gcode_file, 'r') as file:
        for line in file:
            line = line.strip()  # 去掉首尾空白

            # 查找G0/G1指令
            gcode_match = gcode_pattern.match(line)
            if gcode_match:
                g_code = gcode_match.group(1)
                f_value = gcode_match.group(2)
                x = gcode_match.group(3)
                y = gcode_match.group(4)
                z = gcode_match.group(5)

                # 仅保留坐标的数值部分，例如将 "X4" 转换为 "4"
                x = x[1:] if x else None
                y = y[1:] if y else None
                z = z[1:] if z else None

                # 如果X、Y或Z值未提供，使用当前值
                if x is None:
                    x = current_x  # 使用当前X值
                else:
                    current_x = x  # 更新当前X值

                if y is None:
                    y = current_y  # 使用当前Y值
                else:
                    current_y = y  # 更新当前Y值

                if z is None:
                    z = current_z  # 使用当前Z值
                else:
                    current_z = z  # 更新当前Z值

                coordinates.append((g_code, x, y, z))  # 记录指令及坐标
                print(f"提取到指令: {g_code} - F: {f_value}, X: {x}, Y: {y}, Z: {z}")  # 打印提取的指令

    return coordinates


def replace_none_z_values(coordinates):
    """
    遍历坐标列表，替换其中Z为None的值为最后的有效Z值。
    如果之前没有有效的Z值，则将其设置为0。
    """
    current_z = 0  # 初始化为0
    updated_coordinates = []

    for g_code, x, y, z in coordinates:
        if z is not None:
            current_z = z  # 更新当前Z值
        else:
            z = current_z  # 使用最后有效的Z值

        updated_coordinates.append((g_code, x, y, z))

    return updated_coordinates


def save_to_txt(coordinates, output_file):
    """
    将处理后的坐标数据保存为TXT文件。
    """
    with open(output_file, 'w') as file:
        for g_code, x, y, z in coordinates:
            file.write(f"{g_code} - X: {x}, Y: {y}, Z: {z}\n")


def main():
    """
    主程序函数，处理G-code文件的坐标提取、Z值替换和保存。
    """
    # 创建Tkinter主窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 选择G-code文件
    gcode_file_path = filedialog.askopenfilename(title='选择G-code文件', filetypes=[('G-code Files', '*.gcode;*.g')])
    if not gcode_file_path:
        print("未选择文件。")
        return

    # 提取坐标
    coordinates = extract_coordinates(gcode_file_path)

    if not coordinates:
        print("未提取到任何坐标。")
        return

    # 替换Z值
    updated_coordinates = replace_none_z_values(coordinates)

    # 选择输出文件
    output_file_path = filedialog.asksaveasfilename(defaultextension='.txt', title='保存输出文件',
                                                    filetypes=[('Text Files', '*.txt')])
    if not output_file_path:
        print("未选择输出文件。")
        return

    # 保存到TXT文件
    save_to_txt(updated_coordinates, output_file_path)
    print(f"提取并替换后的坐标已保存到 {output_file_path}")


if __name__ == "__main__":
    main()
