import argparse


def process_file(input_file, output_file):
    """
    处理 G-code 文件，在每个以 T1 开头的文本块中复制最后一条 G1 命令并修改 Z 值。

    参数:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    try:
        # 读取输入文件内容
        with open(input_file, 'r') as file:
            lines = file.readlines()

        # 处理文本块
        i = 0
        while i < len(lines):
            if lines[i].startswith('T1'):  # 检测到 T1 开头，开始处理文本块
                block_start = i
                block_end = None

                # 找到文本块的结束（下一个 T0 或 T1）
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('T0') or lines[j].startswith('T1'):
                        block_end = j
                        break

                # 如果找到了文本块的结束
                if block_end is not None:
                    # 获取文本块
                    block_lines = lines[block_start:block_end]

                    # 找到文本块内最后一条 G1 命令
                    last_g1_line = None
                    last_g1_index = -1
                    for index, line in enumerate(reversed(block_lines)):
                        if line.startswith('G1'):
                            last_g1_line = line
                            last_g1_index = len(block_lines) - index - 1
                            break

                    if last_g1_line:
                        # 复制最后一条 G1 命令并修改 Z 值
                        parts = last_g1_line.split()
                        new_parts = []
                        for part in parts:
                            if part.startswith('Z'):
                                # 增加 Z 值 10 并保留 3 位小数
                                new_parts.append(f"Z{round(float(part[1:]) + 10, 3)}")
                            else:
                                new_parts.append(part)

                        # 将修改后的行插入到最后一条 G1 命令后面
                        lines.insert(block_start + last_g1_index + 1, ' '.join(new_parts) + '\n')
                        # 跳到块的结束位置
                        i = block_end
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1

        # 将修改后的内容写入输出文件
        with open(output_file, 'w') as file:
            file.writelines(lines)
        print("文件处理完成！")
    except Exception as e:
        print(f"处理文件时出错: {e}")


def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理 G-code 文件，在 T1 块中复制并修改最后一条 G1 命令的 Z 值")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    args = parser.parse_args()

    # 调用处理函数
    process_file(args.input, args.output)


if __name__ == "__main__":
    main()