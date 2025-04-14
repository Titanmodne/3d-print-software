import re
import argparse

def process_gcode(input_path, output_path, offset_x, offset_y, offset_z):
    """
    读取 G-code 文件，按空行分块处理。
    对包含 T1 的文本块中以 G0 或 G1 开头的行，调整 X、Y、Z 坐标。
    """
    try:
        with open(input_path, 'r') as f:
            content = f.read()
    except Exception as e:
        raise Exception(f"无法读取输入文件：{e}")

    # 按空行分割成多个文本块
    blocks = re.split(r'\n\s*\n', content)
    new_blocks = []

    for block in blocks:
        # 如果该文本块包含 T1，则进行坐标偏移处理
        if 'T1' in block:
            new_lines = []
            for line in block.splitlines():
                # 对以 G0 或 G1 开头的行进行处理
                if line.startswith(('G0', 'G1')):
                    # 替换 X、Y、Z 坐标
                    def replace_coord(match):
                        coord_type = match.group(1)  # X, Y 或 Z
                        coord_value = match.group(2)  # 数字部分
                        if coord_value:  # 确保有数值
                            try:
                                value = float(coord_value)
                                if coord_type == 'X':
                                    new_value = value + offset_x
                                elif coord_type == 'Y':
                                    new_value = value + offset_y
                                elif coord_type == 'Z':
                                    new_value = value + offset_z
                                return f"{coord_type}{new_value:.2f}"
                            except ValueError:
                                return match.group(0)  # 如果转换失败，保持原样
                        return match.group(0)  # 如果没有数值，保持原样

                    line = re.sub(r'([XYZ])(-?\d+\.?\d*)', replace_coord, line)
                new_lines.append(line)
            new_block = "\n".join(new_lines)
        else:
            new_block = block
        new_blocks.append(new_block)

    # 组合所有文本块
    new_content = "\n\n".join(new_blocks)

    try:
        with open(output_path, 'w') as f:
            f.write(new_content)
    except Exception as e:
        raise Exception(f"无法写入输出文件：{e}")

    print("G-code 处理完成！")

# 命令行接口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="处理 G-code 文件，调整坐标偏移量")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--offset_x', type=float, default=3.04, help='X 偏移量')
    parser.add_argument('--offset_y', type=float, default=-56.471, help='Y 偏移量')
    parser.add_argument('--offset_z', type=float, default=-3.11, help='Z 偏移量')
    args = parser.parse_args()

    try:
        process_gcode(args.input, args.output, args.offset_x, args.offset_y, args.offset_z)
    except Exception as e:
        print(f"错误: {e}")