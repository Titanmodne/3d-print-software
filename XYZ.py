import re

def extract_coordinates(gcode_file):
    """
    提取G-code文件中的坐标，并处理Z值的缺失情况。
    如果之前没有有效的X、Y、Z值，则将其设置为0。
    """
    coordinates = []
    current_x = 0  # 当前的X值，初始为0
    current_y = 0  # 当前的Y值，初始为0
    current_z = 0  # 当前的Z值，初始为0

    gcode_pattern = re.compile(
        r'^(G[01])\s*(F[+-]?\d*\.?\d+)?\s*(X[+-]?\d*\.?\d+)?\s*(Y[+-]?\d*\.?\d+)?\s*(Z[+-]?\d*\.?\d+)?', re.MULTILINE)

    with open(gcode_file, 'r') as file:
        for line in file:
            line = line.strip()
            gcode_match = gcode_pattern.match(line)
            if gcode_match:
                g_code, f_value, x, y, z = gcode_match.groups()
                x = x[1:] if x else current_x
                y = y[1:] if y else current_y
                z = z[1:] if z else current_z
                current_x, current_y, current_z = x, y, z
                coordinates.append((g_code, x, y, z))

    return coordinates

def replace_none_z_values(coordinates):
    """
    遍历坐标列表，替换其中Z为None的值为最后的有效Z值。
    如果之前没有有效的Z值，则将其设置为0。
    """
    current_z = 0
    updated_coordinates = []
    for g_code, x, y, z in coordinates:
        z = z or current_z
        current_z = z
        updated_coordinates.append((g_code, x, y, z))
    return updated_coordinates

def save_to_txt(coordinates, output_file):
    """
    将处理后的坐标数据保存为TXT文件。
    """
    with open(output_file, 'w') as file:
        for g_code, x, y, z in coordinates:
            file.write(f"{g_code} X: {x}, Y: {y}, Z: {z}\n")

def process_gcode(gcode_file_path, output_file_path):
    """
    处理G-code文件的坐标提取、Z值替换和保存。
    """
    coordinates = extract_coordinates(gcode_file_path)
    updated_coordinates = replace_none_z_values(coordinates)
    save_to_txt(updated_coordinates, output_file_path)

