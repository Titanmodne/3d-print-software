import argparse


def process_file(input_file, output_file, x_offset, y_offset, j_offset):
    """
    处理 G-code 文件，根据偏置值修改指定块的 G1 命令。

    参数:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        x_offset (float): X 偏移量
        y_offset (float): Y 偏移量
        j_offset (float): J 偏移量
    """
    try:
        # 读取输入文件内容
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分割文本块，使用空行分割
        blocks = content.split('\n\n')
        processed_blocks = []

        # 记录 T1 块的索引
        t1_block_indices = []

        # 遍历每个块，识别 T1 块
        for block_index, block in enumerate(blocks):
            if not block.strip():
                continue  # 跳过空白块

            lines = block.split('\n')
            if not lines:
                continue

            # 检查第一行是否以 T1 开头
            if lines[0].strip().startswith('T1'):
                t1_block_indices.append(block_index)

        # 处理每个 T1 块
        for t1_block_index in t1_block_indices:
            # 获取当前 T1 块
            t1_block = blocks[t1_block_index]
            t1_lines = t1_block.split('\n')

            # 获取下一个块，如果存在
            if t1_block_index + 1 < len(blocks):
                next_block = blocks[t1_block_index + 1]
                next_block_lines = next_block.split('\n')

                # 寻找下一个块中的第一条 G1 行
                g1_line = None
                for line in next_block_lines:
                    if line.strip().startswith('G1'):
                        g1_line = line.strip()
                        break

                if g1_line:
                    # 提取 XY 坐标值
                    x_value = extract_parameter(g1_line, 'X')
                    y_value = extract_parameter(g1_line, 'Y')

                    # 将提取的 X 和 Y 值加上偏移
                    x_value_with_offset = x_value + x_offset if x_value is not None else None
                    y_value_with_offset = y_value + y_offset if y_value is not None else None

                    if x_value_with_offset is None or y_value_with_offset is None:
                        continue

                    # 获取当前块的最后一条 G1 行
                    last_g1_line = None
                    for line in reversed(t1_lines):
                        if line.strip().startswith('G1'):
                            last_g1_line = line.strip()
                            break

                    if last_g1_line:
                        # 提取 Z、J/E、F 值
                        z_value = extract_parameter(last_g1_line, 'Z')
                        j_value = extract_parameter(last_g1_line, 'J')
                        e_value = extract_parameter(last_g1_line, 'E')
                        f_value = extract_parameter(last_g1_line, 'F')

                        # 确定 J/E 的值
                        selected_j = j_value if j_value is not None else e_value

                        # 确定 J 值加上偏移
                        if selected_j is not None:
                            selected_j_with_offset = selected_j + j_offset

                        # 构建新的 G1 行
                        new_g1_parts = ["G1"]  # 添加 G1 指令开头
                        if x_value_with_offset is not None:
                            new_g1_parts.append(f"X{x_value_with_offset:.2f}")
                        if y_value_with_offset is not None:
                            new_g1_parts.append(f"Y{y_value_with_offset:.2f}")
                        if z_value is not None:
                            new_g1_parts.append(f"Z{z_value}")
                        if selected_j is not None:
                            new_g1_parts.append(f"J{selected_j_with_offset:.2f}")
                        if f_value is not None:
                            new_g1_parts.append(f"F{f_value}")

                        new_g1_line = ' '.join(new_g1_parts)

                        # 将新的 G1 行添加到当前 T1 块的最后
                        new_t1_block = '\n'.join(t1_lines + [new_g1_line])

                        # 更新块
                        blocks[t1_block_index] = new_t1_block

        # 保存处理后的块到输出文件
        result = '\n\n'.join(blocks)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)

        print("文件处理完成！")
        print("输出已保存到：", output_file)
    except Exception as e:
        print(f"处理失败：{str(e)}")


def extract_parameter(line, param):
    """从 G1 行中提取指定参数的值"""
    parts = line.split()
    for part in parts:
        if part.startswith(param):
            try:
                return float(part[1:])
            except ValueError:
                return part[1:]  # 返回原始值，如果无法转换为浮点数
    return None


def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理 G-code 文件，修改 T1 块的 G1 命令")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--x_offset', type=float, required=True, help='X 偏移量')
    parser.add_argument('--y_offset', type=float, required=True, help='Y 偏移量')
    parser.add_argument('--j_offset', type=float, required=True, help='J 偏移量')
    args = parser.parse_args()

    # 调用处理函数
    process_file(args.input, args.output, args.x_offset, args.y_offset, args.j_offset)


if __name__ == "__main__":
    main()