import argparse
import re
import math

def extract_coordinates(input_file):
    """
    从输入文件中提取坐标数据。
    返回：
      - coordinates：列表，每个元素为 (x, y, z) 或 None（表示该行没有坐标）
      - original_lines：原始每行内容列表
    """
    coordinates = []
    original_lines = []
    with open(input_file, 'r') as file:
        for line in file:
            original_line = line.strip()
            original_lines.append(original_line)
            if original_line:
                parts = re.findall(r'X([+-]?\d*\.?\d+)\s*Y([+-]?\d*\.?\d+)\s*Z([+-]?\d*\.?\d+)', original_line)
                if parts:
                    x, y, z = map(float, parts[0])
                    coordinates.append((x, y, z))
                else:
                    coordinates.append(None)
            else:
                coordinates.append(None)
    return coordinates, original_lines

def calculate_distances(coordinates, original_lines, k1, k2, f):
    """
    根据坐标数据计算距离，并根据行中是否含有 T0/T1 决定使用哪种计算方式：
      - T0 之后使用 E 值计算
      - T1 之后使用 J 值计算
    """
    output_lines = []
    accumulated_e = 0  # T0 后累积的 E 值
    accumulated_j = 0  # T1 后累积的 J 值
    previous_coordinate = None
    use_e = True  # 默认从 T0 开始，使用 E 值计算

    for i, coordinate in enumerate(coordinates):
        line = original_lines[i]

        # 检测 T0 或 T1 命令，切换计算方式
        if 'T0' in line:
            use_e = True
            accumulated_j = 0  # 切换到 T0 时重置 J 值
            output_lines.append(line)
            continue
        elif 'T1' in line:
            use_e = False
            accumulated_e = 0  # 切换到 T1 时重置 E 值
            output_lines.append(line)
            continue

        # 对于没有坐标的数据行，直接保留原行，并重置累积值和上一个坐标
        if coordinate is None:
            output_lines.append(line)
            accumulated_e = 0
            accumulated_j = 0
            previous_coordinate = None
            continue

        x, y, z = coordinate
        if previous_coordinate:
            x1, y1, z1 = previous_coordinate
            # 计算 XY 平面内的距离
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
            # 对第一条数据直接设置初始 E 或 J 值为 0
            if use_e:
                modified_line = f"{line} E0.00000 F{f}"
            else:
                modified_line = f"{line} J0.00 F{f}"

        output_lines.append(modified_line)
        previous_coordinate = (x, y, z)

    return output_lines

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

def main():
    parser = argparse.ArgumentParser(
        description="根据输入文件中的坐标数据计算距离，并根据 T0/T1 命令选择不同的计算方式，生成附加 E 或 J 参数。"
    )
    parser.add_argument("input_file", type=str, help="输入文件路径")
    parser.add_argument("output_file", type=str, help="输出文件路径")
    parser.add_argument("k1", type=float, help="K1 的值")
    parser.add_argument("k2", type=float, help="K2 的值")
    parser.add_argument("f", type=float, help="F 的值")
    args = parser.parse_args()

    process_jcount(args.input_file, args.output_file, args.k1, args.k2, args.f)

if __name__ == "__main__":
    main()
