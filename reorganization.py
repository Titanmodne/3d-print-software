import argparse
import re


# 处理G-code文件
def process_file(input_file, output_file, type_map):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    print(f"读取文件内容的前5行: {lines[:5]}")

    # 处理每一行数据
    updated_lines = []
    for line in lines:
        # 检查每行是否包含";TYPE:"，如果是则进行处理
        if ";TYPE:" in line:
            match = re.search(r';TYPE:(\S+)', line)
            if match:
                type_name = match.group(1)
                t_value = type_map.get(type_name, "T1")  # 默认T1
                updated_lines.append(f"{t_value}\n")  # 在TYPE行前插入T0或T1
                updated_lines.append(line)  # 写入原始的TYPE行
            else:
                updated_lines.append(line)  # 如果没有找到TYPE，原样写入
        else:
            updated_lines.append(line)  # 非TYPE行直接写入

    # 将修改后的内容写回文件或输出到新的文件
    with open(output_file, 'w') as f:
        f.writelines(updated_lines)
    print(f"文件处理完成，保存为 '{output_file}'")


# 主函数
def main():
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="处理G-code文件中的 TYPE 数据并修改T0或T1")
    parser.add_argument('input_file', type=str, help="输入文件路径")
    parser.add_argument('output_file', type=str, help="输出文件路径")

    # 传入type映射字典
    type_map = {
        'FILL': 'T0',
        'WALL-INNER': 'T1',
        'WALL-OUTER': 'T1',
        'SUPPORT': 'T1',
        'SUPPORT-INTERFACE': 'T1',
        'SKIN': 'T0',
        'SKIRT': 'T0',
    }

    args = parser.parse_args()

    # 处理文件
    process_file(args.input_file, args.output_file, type_map)


if __name__ == "__main__":
    main()
