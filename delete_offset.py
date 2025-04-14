import argparse


def process_gcode(input_file, output_file):
    result = []

    # 读取输入文件的所有行
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    delete_next_line = False  # 标记是否需要删除下一行
    delete_next_two_lines = False  # 标记是否需要删除前后两行（当前代码中未使用）
    first_t0 = True  # 标记是否为第一个 T0
    first_t1 = True  # 标记是否为第一个 T1

    for idx, line in enumerate(lines):
        line = line.strip()

        # 检查 T0 和 T1，处理不同情况
        if line == "T0":
            if first_t0:
                result.append(line + "\n")  # 保留第一个 T0
                first_t0 = False
            else:
                if idx - 1 >= 0 and result:
                    result.pop()  # 删除前一行
                result.append(line + "\n")
        elif line == "T1":
            if first_t1:
                # 第一个 T1 需要删除前一行，并删除下一行
                if idx - 1 >= 0 and result:
                    result.pop()  # 删除前一行
                delete_next_line = True  # 标记删除下一行
                result.append(line + "\n")
                first_t1 = False
            else:
                if idx - 1 >= 0 and result:
                    result.pop()  # 删除前一行
                result.append(line + "\n")
        else:
            # 如果标记删除下一行，则跳过当前行
            if delete_next_line:
                delete_next_line = False
                continue

            # 如果标记删除前后两行，则跳过当前行（本代码未使用该标记）
            if delete_next_two_lines:
                delete_next_two_lines = False
                continue

            # 将非 T0/T1 行加入结果
            result.append(line + "\n")

    # 写入处理后的内容到输出文件
    with open(output_file, 'w') as outfile:
        outfile.writelines(result)


def main():
    parser = argparse.ArgumentParser(
        description="命令行版本 GCODE 处理工具，处理 T0/T1 行及其前后行删除逻辑。"
    )
    parser.add_argument('input_file', type=str, help="输入文件路径")
    parser.add_argument('output_file', type=str, help="输出文件路径")
    args = parser.parse_args()

    process_gcode(args.input_file, args.output_file)
    print(f"Processing Complete! Output saved to: {args.output_file}")


if __name__ == "__main__":
    main()
