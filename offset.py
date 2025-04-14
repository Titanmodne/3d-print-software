import re
import sys
import os


def process_gcode_with_offset(input_file, output_file, target_x, target_y, target_z):
    """
    处理 G-code 文件，根据目标 XYZ 坐标调整所有点的坐标，同时保留 J 挤出量和 F 速度。

    参数：
    - input_file: 输入的 G-code 文件路径
    - output_file: 输出的 G-code 文件路径
    - target_x: 目标 X 坐标
    - target_y: 目标 Y 坐标
    - target_z: 目标 Z 坐标
    """
    # 定义正则表达式，匹配 G0/G1 行中的 XYZ、E、J、F 参数
    gcode_pattern = r"^(G0|G1)(.*)$"  # 捕获 G0/G1 和剩余部分
    param_pattern = r"([XYZEFJ])([-]?\d+\.?\d*)"  # 匹配所有参数

    # 存储第一个有效的 XYZ 坐标
    first_x = first_y = first_z = None

    # 读取输入文件
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # 找到第一个有效的 XYZ 坐标
    for line in lines:
        match = re.match(gcode_pattern, line.strip())
        if match:
            g_command, params = match.groups()
            param_matches = re.findall(param_pattern, params)
            x = y = z = None
            for param_type, param_value in param_matches:
                if param_type == 'X':
                    x = float(param_value)
                elif param_type == 'Y':
                    y = float(param_value)
                elif param_type == 'Z':
                    z = float(param_value)
            if x is not None and y is not None and z is not None:
                first_x = x
                first_y = y
                first_z = z
                break

    if first_x is None or first_y is None or first_z is None:
        print("错误：文件中未找到有效的 XYZ 坐标点！")
        sys.exit(1)

    # 计算差值
    offset_x = target_x - first_x
    offset_y = target_y - first_y
    offset_z = target_z - first_z

    print(f"计算得到的偏移量：X={offset_x}, Y={offset_y}, Z={offset_z}")

    # 处理文件并写入输出文件
    with open(output_file, 'w') as f:
        for line in lines:
            match = re.match(gcode_pattern, line.strip())
            if match:
                g_command, params = match.groups()
                param_matches = re.findall(param_pattern, params)

                # 初始化新参数字典
                new_params = {}
                for param_type, param_value in param_matches:
                    if param_type == 'X':
                        new_params['X'] = float(param_value) + offset_x
                    elif param_type == 'Y':
                        new_params['Y'] = float(param_value) + offset_y
                    elif param_type == 'Z':
                        new_params['Z'] = float(param_value) + offset_z
                    else:
                        # 保留 E、J、F 参数不变
                        new_params[param_type] = param_value

                # 构建新的 G-code 行
                new_line = g_command
                for param_type in ['X', 'Y', 'Z', 'E', 'J', 'F']:
                    if param_type in new_params:
                        if param_type in ['X', 'Y', 'Z']:
                            new_line += f" {param_type}{new_params[param_type]:.5f}"
                        else:
                            new_line += f" {param_type}{new_params[param_type]}"
                new_line += "\n"
                f.write(new_line)
            else:
                # 非 G0/G1 行保持不变
                f.write(line)

    print(f"处理完成！输出文件已保存至：{output_file}")


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) != 6:
        print("用法：python script.py <input_file> <output_file> <target_x> <target_y> <target_z>")
        print("示例：python script.py input.gcode output.gcode 100.0 200.0 0.0")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    try:
        target_x = float(sys.argv[3])
        target_y = float(sys.argv[4])
        target_z = float(sys.argv[5])
    except ValueError:
        print("错误：目标坐标 X、Y、Z 必须是数字！")
        sys.exit(1)

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误：输入文件 '{input_file}' 不存在！")
        sys.exit(1)

    # 执行处理
    process_gcode_with_offset(input_file, output_file, target_x, target_y, target_z)