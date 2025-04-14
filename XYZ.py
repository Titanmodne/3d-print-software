import re

def extract_coordinates(input_path):
    """
    从 G-code 文件中提取坐标，并处理 Z 值和 E 值的缺失情况。
    """
    coordinates = []
    current_x = current_y = current_z = 0  # 初始化坐标为0
    current_e = None  # 初始化 E 值为 None

    gcode_pattern = re.compile(
        r'^(G[01])\s*(F[+-]?\d*\.?\d+)?\s*(X[+-]?\d*\.?\d+)?\s*(Y[+-]?\d*\.?\d+)?\s*(Z[+-]?\d*\.?\d+)?\s*(E[+-]?\d*\.?\d+)?',
        re.MULTILINE)

    with open(input_path, 'r') as file:
        for line in file:
            line = line.strip()
            gcode_match = gcode_pattern.match(line)
            if gcode_match:
                g_code, f_value, x, y, z, e = gcode_match.groups()
                x = float(x[1:]) if x else current_x
                y = float(y[1:]) if y else current_y
                z = float(z[1:]) if z else current_z
                e = float(e[1:]) if e else current_e
                current_x, current_y, current_z, current_e = x, y, z, e
                coordinates.append((g_code, x, y, z, e))
    return coordinates

def remove_first_n_entries(coordinates, n):
    """
    删除坐标列表中的前N条数据。
    """
    return coordinates[n:]

def replace_none_z_values(coordinates):
    """
    替换其中Z为None的值为最后的有效Z值，并在以下情况插入空行：
    1. Z值变化；
    2. E值下降；
    3. 检测不到 E 值；
    4. G-code 为 G0（快速移动指令）。
    """
    current_z = 0.0  # 默认 Z 为 0.0
    current_e = None  # 初始化 E 为 None
    updated_coordinates = []

    for g_code, x, y, z, e in coordinates:
        # 确保 Z 和 E 有默认值
        z = float(z) if z is not None else current_z
        e = float(e) if e is not None else None

        # 插入空行的条件：
        if (
            e is None or  # E 值缺失
            z != current_z or  # Z 值变化
            (current_e is not None and e is not None and e < current_e) or  # E 值下降
            g_code == "G0"  # G0 指令
        ):
            updated_coordinates.append(None)  # 插入空行

        # 更新当前的 Z 和 E 值
        current_z = z
        current_e = e

        updated_coordinates.append((g_code, x, y, z, e))

    return updated_coordinates


def remove_single_data_between_empty_lines(coordinates):
    """
    删除两个空行之间只有一条数据的情况。
    """
    cleaned_coordinates = []
    buffer = []
    for item in coordinates:
        if item is None:
            if len(buffer) == 1:
                buffer = []
            else:
                cleaned_coordinates.extend(buffer)
                cleaned_coordinates.append(None)
                buffer = []
        else:
            buffer.append(item)
    if len(buffer) > 1:
        cleaned_coordinates.extend(buffer)
    return cleaned_coordinates

def save_to_txt(coordinates, output_file):
    """
    将处理后的坐标数据保存为TXT文件。
    """
    with open(output_file, 'w') as file:
        for line in coordinates:
            if line is None:
                file.write("\n")
            else:
                g_code, x, y, z, _ = line  # 忽略E值
                file.write(f"{g_code} X: {x}, Y: {y}, Z: {z}\n")

def remove_z_below_threshold(coordinates, threshold=0.05):
    """
    删除 Z 值低于指定阈值的行。
    """
    return [coord for coord in coordinates if coord is None or coord[3] >= threshold]

def remove_empty_lines_at_start(coordinates):
    """
    删除开头连续的空行，直到第一行不是空行为止。
    """
    while coordinates and coordinates[0] is None:
        coordinates.pop(0)
    return coordinates

def process_gcode(input_path, output_path):
    """
    处理 G-code 文件，并保存处理后的结果到指定路径。
    """
    coordinates = extract_coordinates(input_path)
    # 删除前三条数据
    coordinates = remove_first_n_entries(coordinates, 3)
    # 进行后续处理
    updated_coordinates = replace_none_z_values(coordinates)
    cleaned_coordinates = remove_single_data_between_empty_lines(updated_coordinates)
    # 删除 Z 值低于 0.05 的行
    filtered_coordinates = remove_z_below_threshold(cleaned_coordinates, threshold=0.05)
    # 删除开头的空行
    final_coordinates = remove_empty_lines_at_start(filtered_coordinates)
    # 保存到 TXT 文件
    save_to_txt(final_coordinates, output_path)