import re
import math
import sys

def calculate_distance(coord1, coord2):
    """
    计算两个坐标点之间的欧几里得距离
    :param coord1: 第一个坐标点 (x1, y1, z1)
    :param coord2: 第二个坐标点 (x2, y2, z2)
    :return: 两个坐标点之间的距离
    """
    return math.sqrt((coord2[0] - coord1[0]) ** 2 +
                     (coord2[1] - coord1[1]) ** 2 +
                     (coord2[2] - coord1[2]) ** 2)


def parse_line(line):
    """
    从G-code的每一行中提取 X, Y, Z 的值。
    :param line: 一行G-code字符串
    :return: 返回 (X, Y, Z) 坐标元组，如果没有匹配到则返回 None
    """
    # 正则表达式匹配 X:, Y:, Z: 后面的值
    parts = re.findall(r'X:\s*([+-]?\d*\.?\d+)\s*,\s*Y:\s*([+-]?\d*\.?\d+)\s*,\s*Z:\s*([+-]?\d*\.?\d+)', line)
    if parts:
        x, y, z = map(float, parts[0])  # 将匹配到的值转为浮动点数
        return x, y, z
    return None


def parse_blocks(content):
    """
    解析G-code文件内容，将其按空行分块
    :param content: G-code文件的全部内容（字符串）
    :return: 返回分块后的文本块列表，每个块是一个列表，包含该块内的每行G-code
    """
    blocks = content.strip().split("\n\n")  # 按空行分割
    parsed_blocks = []
    for block in blocks:
        lines = block.strip().split("\n")  # 按行分割
        if lines:
            parsed_blocks.append(lines)  # 添加到解析块列表中
    return parsed_blocks


def merge_blocks_if_close(parsed_blocks, threshold):
    """
    如果前一个文本块的最后一行和下一个文本块的第一行之间的距离小于阈值的1.5倍，则删除这两个文本块之间的空行
    :param parsed_blocks: 解析后的文本块列表
    :param threshold: 距离阈值
    :return: 返回合并后的完整内容
    """
    merged_blocks = []
    i = 0
    while i < len(parsed_blocks) - 1:
        lines1 = parsed_blocks[i]
        lines2 = parsed_blocks[i + 1]

        # 提取前一个块最后一行的坐标
        last_coords = parse_line(lines1[-1])
        # 提取下一个块第一行的坐标
        first_coords = parse_line(lines2[0])

        if last_coords and first_coords:
            distance = calculate_distance(last_coords, first_coords)
            # 判断前后两块的距离是否小于阈值的1.5倍
            if distance < threshold * 1.5:
                # 合并这两个文本块并去掉空行
                merged_lines = lines1 + lines2
                parsed_blocks[i + 1] = merged_lines
            else:
                merged_blocks.append("\n".join(lines1))  # 如果不合并，保持原样
        i += 1

    # 添加最后一个块
    merged_blocks.append("\n".join(parsed_blocks[-1]))
    return "\n\n".join(merged_blocks)


def process_gcode_file(input_path, output_path, threshold):
    """
    处理G-code文件，按照距离阈值合并文本块，并保存到输出文件
    :param input_path: 输入文件路径
    :param output_path: 输出文件路径
    :param threshold: 合并的距离阈值
    """
    with open(input_path, 'r') as file:
        content = file.read()  # 读取文件内容

    parsed_blocks = parse_blocks(content)  # 解析文件内容为文本块
    merged_content = merge_blocks_if_close(parsed_blocks, threshold)  # 合并符合条件的文本块

    with open(output_path, 'w') as file:
        file.write(merged_content)  # 保存合并后的内容到输出文件


def main():
    """
    通过命令行参数选择输入文件和输出文件，输入距离阈值，并处理 G-code 文件。
    """
    if len(sys.argv) != 4:
        print("Usage: python script.py <input_file> <output_file> <threshold>")
        sys.exit(1)

    input_path = sys.argv[1]  # 输入文件路径
    output_path = sys.argv[2]  # 输出文件路径
    threshold = float(sys.argv[3])  # 距离阈值

    # 处理G-code文件
    process_gcode_file(input_path, output_path, threshold)
    print(f"处理完成，输出文件保存为：{output_path}")


if __name__ == "__main__":
    main()
