import argparse

def remove_continuous_g0(data):
    """移除连续的 G0 指令"""
    result = []
    g0_lines = []  # 存储连续的 G0 指令

    for line in data:
        stripped_line = line.strip()
        if stripped_line.startswith("G0"):
            g0_lines.append(line)  # 收集 G0 指令
        else:
            # 处理前面的连续 G0 指令
            if len(g0_lines) > 1:
                result.append(g0_lines[-1])  # 只保留最后一个 G0
            elif len(g0_lines) == 1:
                result.append(g0_lines[0])  # 保留单个 G0
            g0_lines = []  # 重置 G0 列表
            result.append(line)  # 添加当前行（可能是空行或非 G0 行）

    # 处理数据块末尾的连续 G0
    if len(g0_lines) > 1:
        result.append(g0_lines[-1])  # 只保留最后一个 G0
    elif len(g0_lines) == 1:
        result.append(g0_lines[0])  # 保留单个 G0

    return result

def process_file(input_path, output_path):
    """处理 G-code 文件，删除非 T0 块中的连续 G0 指令，并保留原有空行"""
    try:
        with open(input_path, 'r') as file:
            lines = file.readlines()  # 读取所有行，保留换行符

        processed_data = []
        block = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line == "":
                # 遇到空行，处理当前数据块并添加空行
                if block:
                    if block[0].strip().startswith("T0"):
                        processed_data.extend(block)  # T0 块保持不变
                    else:
                        processed_data.extend(remove_continuous_g0(block))  # 删除连续 G0
                    block = []
                processed_data.append("")  # 保留原始空行
            else:
                block.append(line.rstrip('\n'))  # 去掉换行符，稍后统一处理

        # 处理最后一个数据块
        if block:
            if block[0].strip().startswith("T0"):
                processed_data.extend(block)
            else:
                processed_data.extend(remove_continuous_g0(block))

        # 写入输出文件，保留原始换行符
        with open(output_path, 'w') as file:
            for line in processed_data:
                file.write(line + "\n")  # 统一添加换行符

        print("文件处理完成！")

    except FileNotFoundError:
        print(f"错误：输入文件 {input_path} 不存在")
    except Exception as e:
        print(f"处理文件时出错: {e}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理 G-code 文件，删除连续的 G0 指令")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    args = parser.parse_args()

    # 调用处理函数
    process_file(args.input, args.output)

if __name__ == "__main__":
    main()