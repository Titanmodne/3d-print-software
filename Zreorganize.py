import re
import argparse

def process_z_values(input_path, output_path):
    """
    处理文本文件，确保每个由空行分隔的文本块中的Z值一致。
    如果发现不一致的Z值，则统一修改为该文本块中的第一个Z值。
    保留输入文件中的空行结构。

    参数:
        input_path (str): 输入文件路径
        output_path (str): 输出文件路径
    """
    # 读取输入文件
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
    except Exception as e:
        raise Exception(f"无法读取输入文件：{e}")

    processed_lines = []  # 存储处理后的行
    block = []  # 当前文本块
    first_z = None  # 文本块中的第一个Z值

    # 逐行处理
    for line in lines:
        stripped_line = line.strip()
        if stripped_line == "":
            # 遇到空行，处理当前文本块并保留空行
            if block:
                processed_lines.extend(process_block(block, first_z))
            processed_lines.append(line)  # 直接保留原始空行（包含换行符）
            block = []
            first_z = None
        else:
            block.append(line)
            # 提取Z值，仅用于确定第一个Z值
            z_match = re.search(r'Z([+-]?\d*\.?\d+)', line)
            if z_match and first_z is None:
                first_z = float(z_match.group(1))

    # 处理最后一个文本块
    if block:
        processed_lines.extend(process_block(block, first_z))

    # 写入输出文件
    try:
        with open(output_path, 'w') as f:
            for line in processed_lines:
                f.write(line)
    except Exception as e:
        raise Exception(f"无法写入输出文件：{e}")

    print("文本处理完成！")

def process_block(block, first_z):
    """
    处理单个文本块，确保所有Z值与第一个Z值一致。

    参数:
        block (list): 文本块的行列表
        first_z (float): 文本块中的第一个Z值

    返回:
        list: 处理后的文本块行列表
    """
    if first_z is None:
        return block  # 没有Z值，保持不变

    processed_block = []
    for line in block:
        z_match = re.search(r'Z([+-]?\d*\.?\d+)', line)
        if z_match:
            current_z = float(z_match.group(1))
            if current_z != first_z:
                line = re.sub(r'Z[+-]?\d*\.?\d+', f'Z{first_z:.2f}', line)
        processed_block.append(line)
    return processed_block

# 命令行接口
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="处理文本文件，确保每个文本块的Z值一致")
    parser.add_argument('--input', required=True, help='输入文件路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    args = parser.parse_args()

    try:
        process_z_values(args.input, args.output)
    except Exception as e:
        print(f"错误: {e}")