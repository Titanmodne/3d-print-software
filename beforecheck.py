import sys
import re


def process_gcode_file(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    output_lines = []
    in_t1_block = False
    prev_j_value = None
    j_offset = 0.0  # 用于记录当前段的J值偏移量

    for line in lines:
        line = line.strip()

        # 检查是否是T1开始的数据块
        if line.startswith('T1'):
            in_t1_block = True
            j_offset = 0.0  # 重置偏移量
            output_lines.append(line)
            continue
        # 检查是否是T0或其他打印头，结束T1检测
        elif line.startswith('T0'):
            in_t1_block = False
            j_offset = 0.0  # 重置偏移量
            output_lines.append(line)
            continue

        # 如果在T1块中
        if in_t1_block:
            # 提取当前行的J值（如果有）
            j_match = re.search(r'J([\d.]+)', line)
            current_j = float(j_match.group(1)) if j_match else None

            # 如果当前行有J值
            if current_j is not None:
                # 如果与前一个J值相等
                if prev_j_value is not None and abs(current_j - prev_j_value) < 0.0001:
                    # 添加空行、打印头和类型
                    output_lines.append('')
                    output_lines.append('T1')
                    # 查找上一条TYPE行
                    for prev_line in reversed(output_lines):
                        if prev_line.startswith(';TYPE:'):
                            output_lines.append(prev_line)
                            break
                    # 更新J值偏移量，从这行开始重新计算
                    j_offset = current_j

                # 处理当前行的J值（无论是否分割，都应用偏移量）
                new_j = current_j - j_offset
                line = re.sub(r'J[\d.]+', f'J{new_j:.2f}', line)

                # 更新prev_j_value
                prev_j_value = current_j

        output_lines.append(line)

    # 写入输出文件
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py input.gcode output.gcode")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        process_gcode_file(input_file, output_file)
        print(f"Processing complete. Output written to {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()