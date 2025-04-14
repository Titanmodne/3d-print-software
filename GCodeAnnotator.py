import re

def process_gcode(input_path, output_path):
    """处理 G-code 文件，添加空行、打印头类型和打印类型"""
    try:
        with open(input_path, 'r') as infile:
            lines = infile.readlines()

        new_lines = []
        current_type = ""
        current_head = ""

        for line in lines:
            # 识别打印头类型
            if "T0" in line:
                current_head = "T0"
            elif "T1" in line:
                current_head = "T1"

            # 识别打印类型
            match = re.search(r';TYPE:(\S+)', line)
            if match:
                current_type = match.group(1)

            # 在特定 G0 指令前添加空行、打印头类型和打印类型
            if line.startswith("G0 F15000"):
                new_lines.append("\n")  # 添加空行
                new_lines.append(f"{current_head}\n")  # 打印头类型
                new_lines.append(f";TYPE:{current_type}\n")  # 打印类型

            # 添加其他数据行
            new_lines.append(line)

        # 写入新的 G-code 文件
        with open(output_path, 'w') as outfile:
            outfile.writelines(new_lines)
        print("G-code 处理完成！")
    except Exception as e:
        raise Exception(f"处理 G-code 文件时出错: {e}")

# 可选：添加命令行接口（独立运行时使用）
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("用法: python GCodeAnnotator.py <输入文件> <输出文件>")
    else:
        process_gcode(sys.argv[1], sys.argv[2])