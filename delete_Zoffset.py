import argparse
import re

def process_file(input_text):
    """
    按行处理输入文本，比较连续两行中G0/G1指令的Z值，
    如果当前行的Z值大于下一行的Z值，则删除当前行；
    同时在G0/G1指令块结束后（下一行不再以G0或G1开头时）插入一个空行。
    """
    lines = input_text.splitlines()
    result_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 处理G0/G1指令的块
        if line.startswith(('G0', 'G1')):
            # 如果有下一行，则比较当前行和下一行的Z值
            if i + 1 < len(lines):
                match1 = re.search(r'Z([+-]?[0-9]*\.?[0-9]+)', lines[i])
                match2 = re.search(r'Z([+-]?[0-9]*\.?[0-9]+)', lines[i + 1])
                if match1 and match2:
                    z1 = float(match1.group(1))
                    z2 = float(match2.group(1))
                    # 如果当前行的Z值大于下一行的Z值，则跳过当前行
                    if z1 > z2:
                        i += 1
                        continue

            # 将有效行加入结果
            result_lines.append(line)

            # 检查下一行是否不是G0/G1指令，如果是，则添加一个空行
            if i + 1 < len(lines) and not lines[i + 1].startswith(('G0', 'G1')):
                result_lines.append("")  # 添加空行

        else:
            result_lines.append(line)

        i += 1

    return '\n'.join(result_lines)


def main():
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(
        description="处理文本文件：根据G0/G1指令中Z值比较删除某些行，并在必要时插入空行。"
    )
    parser.add_argument("input_file", type=str, help="输入文件路径")
    parser.add_argument("output_file", type=str, help="输出文件路径")
    args = parser.parse_args()

    # 读取输入文件
    with open(args.input_file, 'r') as infile:
        input_text = infile.read()

    # 处理数据
    output_text = process_file(input_text)

    # 将处理后的内容写入输出文件
    with open(args.output_file, 'w') as outfile:
        outfile.write(output_text)

    print(f"处理完成，结果已保存到: {args.output_file}")


if __name__ == "__main__":
    main()
