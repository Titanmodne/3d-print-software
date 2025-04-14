import argparse


def process_file(input_file, output_file, f_value):
    """
    处理 G-code 文件，替换 T1 块中前四个 G1 命令的 F 值。

    参数:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
        f_value (float): 要替换的 F 值
    """
    try:
        # 读取输入文件
        with open(input_file, 'r') as file:
            lines = file.readlines()

        # 遍历文件行，找到 T1 并处理后续 G1 命令
        for i in range(len(lines)):
            if lines[i].startswith('T1'):
                count = 0
                # 从 T1 后的行开始，替换前四个 G1 的 F 值
                for j in range(i + 1, len(lines)):
                    # 跳过 T0 或以 ;TYPE: 开头的行
                    if lines[j].startswith('T0') or lines[j].startswith(';TYPE:'):
                        continue
                    # 处理包含 G1 和 F 的行
                    if 'G1' in lines[j] and 'F' in lines[j]:
                        parts = lines[j].split()
                        for k in range(len(parts)):
                            if parts[k].startswith('F'):
                                parts[k] = f"F{f_value}"
                        lines[j] = ' '.join(parts) + '\n'
                        count += 1
                        if count >= 4:  # 只替换前四个 G1
                            break

        # 将修改后的内容写入输出文件
        with open(output_file, 'w') as file:
            file.writelines(lines)
        print("文件处理完成！")
    except Exception as e:
        print(f"处理文件时出错: {e}")


def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理 G-code 文件，替换 T1 块中前四个 G1 命令的 F 值")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--f_value', type=float, required=True, help='替换的 F 值')
    args = parser.parse_args()

    # 调用处理函数
    process_file(args.input, args.output, args.f_value)


if __name__ == "__main__":
    main()