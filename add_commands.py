import argparse

def add_commands_and_swap_T0_T1(file_path, output_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # 在文件开头添加 M211 S0
    lines.insert(0, "M211 S0\n")

    # 创建一个新的列表来存储修改后的行
    new_lines = []

    for line in lines:
        # 如果是T0，在T0前面添加M400和M280 P0 S95
        if 'T0' in line:
            new_lines.append("M400\n")
            new_lines.append("M280 P0 S95\n")
            new_lines.append("M400\n")
            new_lines.append(line.replace('T0', 'TEMP').replace('T1', 'T0').replace('TEMP', 'T1'))
        # 如果是T1，在T1前面添加M400和M280 P0 S2
        elif 'T1' in line:
            new_lines.append("M400\n")
            new_lines.append("M280 P0 S2\n")
            new_lines.append("M400\n")
            new_lines.append(line.replace('T1', 'TEMP').replace('T0', 'T1').replace('TEMP', 'T0'))
        # 如果是;TYPE:语句，在其前面添加G92 E0和G92 J0
        elif ';TYPE:' in line:
            new_lines.append("G92 E0\n")  # 添加G92 E0
            new_lines.append("G92 J0\n")  # 添加G92 J0
            new_lines.append(line)
        else:
            new_lines.append(line)

    # 将修改后的内容写入到输出文件
    with open(output_path, 'w') as file:
        file.writelines(new_lines)

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理 G-code 文件，添加命令并交换 T0 和 T1")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    args = parser.parse_args()

    # 调用处理函数
    add_commands_and_swap_T0_T1(args.input, args.output)
    print("文件处理完成，已保存至:", args.output)

if __name__ == "__main__":
    main()