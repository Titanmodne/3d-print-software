import re
import math

def extract_coordinates(input_file):
    coordinates = []
    original_lines = []
    with open(input_file, 'r') as file:
        for line in file:
            original_line = line.strip()
            original_lines.append(original_line)  # 保留原始行
            if original_line:
                parts = re.findall(r'X: ([+-]?\d*\.?\d+), Y: ([+-]?\d*\.?\d+), Z: ([+-]?\d*\.?\d+)', original_line)
                if parts:
                    x, y, z = map(float, parts[0])
                    coordinates.append((x, y, z))
                else:
                    coordinates.append(None)  # 保存无坐标行为None
            else:
                coordinates.append(None)  # 保存空行为None
    return coordinates, original_lines

def calculate_distances(coordinates, original_lines, c, f):
    output_lines = []
    accumulated_j = 0  # 初始化累加的J值
    previous_coordinate = None

    for i, coordinate in enumerate(coordinates):
        if coordinate is None:
            output_lines.append("")  # 直接添加空行
            accumulated_j = 0  # 检测到空行时重置J值
            previous_coordinate = None  # 清除上一坐标
            continue

        x, y, z = coordinate
        if previous_coordinate:
            x1, y1, z1 = previous_coordinate
            j = math.sqrt((x - x1) ** 2 + (y - y1) ** 2)
            accumulated_j += j * c
            modified_line = f"{original_lines[i]} J: {accumulated_j:.2f} F: {f}"
        else:
            modified_line = f"{original_lines[i]} J: 0.00 F: {f}"  # 对第一条数据直接设置 J 值为 0

        output_lines.append(modified_line)
        previous_coordinate = (x, y, z)

    return output_lines

def process_jcount(input_file_path, output_file_path, k, f):
    coordinates, original_lines = extract_coordinates(input_file_path)
    if not coordinates:
        print("No coordinates extracted.")
        return

    output_lines = calculate_distances(coordinates, original_lines, k, f)

    with open(output_file_path, 'w') as file:
        for line in output_lines:
            file.write(line + "\n")

    print(f"Processed data saved to {output_file_path}")
