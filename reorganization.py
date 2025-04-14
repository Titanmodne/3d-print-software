import re


def process_file(input_file, output_file, type_map):
    """
    处理 G-code 文件，根据 type_map 在指定行插入 T0 或 T1。

    参数:
    - input_file (str): 输入文件路径
    - output_file (str): 输出文件路径
    - type_map (dict): 类型到 T 值 ('T0' 或 'T1') 的映射
    """
    # 读取输入文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise Exception(f"输入文件 {input_file} 不存在")
    except Exception as e:
        raise Exception(f"读取输入文件失败: {str(e)}")

    # 处理并写入输出文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in lines:
                if ";TYPE:" in line:
                    match = re.search(r';TYPE:(\S+)', line)
                    if match:
                        type_name = match.group(1)
                        t_value = type_map.get(type_name, "T1")  # 如果 type_name 不在 type_map 中，默认使用 T1
                        f.write(f"{t_value}\n")  # 在 TYPE 行前插入 T0 或 T1
                        f.write(line)  # 写入原始 TYPE 行
                    else:
                        f.write(line)  # 未匹配到 TYPE，保持原样
                else:
                    f.write(line)  # 非 TYPE 行直接写入
    except Exception as e:
        raise Exception(f"写入输出文件失败: {str(e)}")