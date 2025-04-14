import argparse

def process_file(input_path, output_path):
    """处理 G-code 文件，保留特定行并调整 G0 和 G1 指令顺序"""
    # 读取输入文件
    try:
        with open(input_path, 'r') as infile:
            lines = infile.readlines()
    except FileNotFoundError:
        raise Exception(f"输入文件 {input_path} 不存在")
    except Exception as e:
        raise Exception(f"读取输入文件失败: {str(e)}")

    result = []
    additional_line = None  # 用于存储不带Z坐标的 G0 指令

    # 逐行处理 G-code
    for line in lines:
        line = line.strip()

        # 保存所有的 ;TYPE: 行
        if line.startswith(';TYPE:'):
            result.append(line)  # 添加 ;TYPE: 行
            continue  # 跳过后续处理

        # 处理 T0 和 T1 行
        if line.startswith(('T0', 'T1')):
            result.append(line)  # 添加 T0 或 T1 行
            continue  # 跳过后续处理

        # 处理 G0 指令
        if line.startswith('G0'):
            # 检查是否包含 Z 坐标
            if 'Z' in line:
                result.append(line)  # 直接保留带有 Z 坐标的 G0 行
            else:
                additional_line = line  # 存储不带 Z 坐标的 G0 指令
            continue  # 跳过当前行，等待后续处理

        # 处理 G1 指令
        if line.startswith('G1'):
            if additional_line:  # 如果之前存储了不带 Z 坐标的 G0 指令
                result.append(additional_line)  # 添加 G0 指令
                result.append(line)  # 添加当前的 G1 指令
                additional_line = None  # 清空存储的 G0 指令
            else:
                result.append(line)  # 直接添加 G1 指令

    # 写入结果到输出文件
    try:
        with open(output_path, 'w') as outfile:
            outfile.writelines([line + '\n' for line in result])
    except Exception as e:
        raise Exception(f"写入输出文件失败: {str(e)}")

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="处理 G-code 文件")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    args = parser.parse_args()

    # 调用处理函数并输出结果
    try:
        process_file(args.input, args.output)
        print("文件处理完成！")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()