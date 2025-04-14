import re
import math
import argparse

# 提取坐标的函数
def extract_coordinates(input_file):
    """从G-code文件中提取X、Y、Z坐标"""
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
                    coordinates.append(None)  # 无坐标行为None
            else:
                coordinates.append(None)  # 空行为None
    return coordinates, original_lines

# 计算坐标距离并根据T0和T1选择不同的计算方式

def calculate_distances(coordinates, original_lines, k1, k2, f1, f2):
    """根据T0/T1命令计算E和J值，并生成新的G-code行"""
    output_lines = []
    accumulated_e = 0  # T0后的累积E值
    accumulated_j = 0  # T1后的累积J值
    previous_coordinate = None
    previous_command = None  # 保存前一个命令类型（G0 或 G1）
    use_e = True  # 默认使用E值计算（从T0开始）
    last_valid_e = 0  # 记录上一个有效的E值
    last_valid_j = 0  # 记录上一个有效的J值（新增）

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
            previous_command = None  # 清除前一个命令
            continue

        # 如果前一个命令是G1，当前命令是G0，或者前一个命令是G0，当前命令是G0，则跳过挤出量计算
        if (previous_command == 'G1' and 'G0' in line) or (previous_command == 'G0' and 'G0' in line):
            # 根据当前文本块类型选择使用最后一个有效的E或J值
            if use_e:
                modified_line = f"{line} E{last_valid_e:.5f} F{f1}"
            else:
                modified_line = f"{line} J{last_valid_j:.2f} F{f2}"
            output_lines.append(modified_line)  # 直接保存G1到G0或G0到G0之间的命令
            previous_command = 'G0'
            previous_coordinate = coordinate
            continue

        # 提取坐标并计算距离
        x, y, z = coordinate
        if previous_coordinate:
            x1, y1, z1 = previous_coordinate
            distance = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
            if use_e:
                e = distance * k1
                accumulated_e += e
                modified_line = f"{line} E{accumulated_e:.5f} F{f1}"  # 使用F1
                last_valid_e = accumulated_e  # 更新最后一个有效的E值
            else:
                j = distance * k2  # 直接使用k2计算J值
                accumulated_j += j
                modified_line = f"{line} J{accumulated_j:.2f} F{f2}"  # 使用F2
                last_valid_j = accumulated_j  # 更新最后一个有效的J值
        else:
            # 对第一条数据直接设置E值为0.00或J值为0.00，F值由输入指定
            if use_e:
                modified_line = f"{line} E0.00000 F{f1}"  # 使用F1
                last_valid_e = 0  # 更新最后一个有效的E值
            else:
                modified_line = f"{line} J0.00 F{f2}"  # 使用F2
                last_valid_j = 0  # 更新最后一个有效的J值

        output_lines.append(modified_line)
        previous_command = line.split()[0] if line.split() else None  # 记录当前命令类型
        previous_coordinate = coordinate

    return output_lines

# 处理主程序
def process_jcount(input_file_path, output_file_path, w, h, k2, f1, f2):
    """处理G-code文件，计算并添加E和J值"""
    coordinates, original_lines = extract_coordinates(input_file_path)
    if not coordinates:
        print("未提取到坐标数据.")
        return

    # 计算K1
    k1 = (w * h) / (math.pi * (7 / 8) ** 2)

    # 处理G-code
    output_lines = calculate_distances(coordinates, original_lines, k1, k2, f1, f2)

    # 写入输出文件
    with open(output_file_path, 'w') as file:
        for line in output_lines:
            file.write(line + "\n")

    print(f"处理后的数据已保存到 {output_file_path}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理G-code文件，计算E和J值")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--w', type=float, required=True, help='线宽W')
    parser.add_argument('--h', type=float, required=True, help='层厚H')
    parser.add_argument('--k2', type=float, required=True, help='K2值')
    parser.add_argument('--f1', type=float, required=True, help='F1进给速度')
    parser.add_argument('--f2', type=float, required=True, help='F2进给速度')
    args = parser.parse_args()

    # 调用处理函数
    process_jcount(args.input, args.output, args.w, args.h, args.k2, args.f1, args.f2)

if __name__ == "__main__":
    main()