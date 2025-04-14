import argparse

def process_file(input_file, output_file):
    """
    处理 G-code 文件，在文件末尾添加一条修改后的 G1 命令行。

    参数:
        input_file (str): 输入文件路径
        output_file (str): 输出文件路径
    """
    try:
        # 读取输入文件内容
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 找到最后一条包含 X、Y、Z 的 G1 数据行
        last_data_line = None
        for line in reversed(lines):
            line = line.strip()
            if line.startswith('G1'):
                parts = line.split()
                x = None
                y = None
                z = None
                for part in parts:
                    if part.startswith('X'):
                        x = part[1:]
                    elif part.startswith('Y'):
                        y = part[1:]
                    elif part.startswith('Z'):
                        z = part[1:]
                if x is not None and y is not None and z is not None:
                    last_data_line = line
                    break

        if not last_data_line:
            print("未找到包含 X、Y、Z 的 G1 数据行")
            return

        # 解析数据
        parts = last_data_line.split()
        x = None
        y = None
        z = None
        f = None
        for part in parts:
            if part.startswith('X'):
                x = part[1:]
            elif part.startswith('Y'):
                y = part[1:]
            elif part.startswith('Z'):
                z = part[1:]
            elif part.startswith('F'):
                f = part[1:]

        if not all([x, y, z]):
            print("未找到 X、Y、Z 值")
            return

        # 修改 Z 和 F 值
        z_new = float(z) + 40
        f_new = 300  # 固定修改为 300

        # 生成新行
        new_line = f"G1 X{x} Y{y} Z{z_new:.2f}"
        if f:
            new_line += f" F{f_new}"

        # 写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("".join(lines))
            f.write("\n" + new_line)

        print("处理完成")
    except Exception as e:
        print(f"处理失败：{str(e)}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理 G-code 文件，在末尾添加修改后的 G1 命令行")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    args = parser.parse_args()

    # 调用处理函数
    process_file(args.input, args.output)

if __name__ == "__main__":
    main()