def remove_continuous_g0(data):
    """移除连续的G0指令，仅保留最后一个G0"""
    result = []
    g0_lines = []  # 用于存储连续的G0指令
    for line in data:
        if line.startswith("G0"):
            g0_lines.append(line)  # 收集连续的G0指令
        else:
            # 如果遇到非G0指令，先将最后一个G0指令（如果有）加入结果
            if g0_lines:
                result.append(g0_lines[-1])  # 只保留最后一个G0
                g0_lines = []  # 重置G0列表
            result.append(line)  # 添加非G0指令
    # 处理文件末尾的连续G0指令
    if g0_lines:
        result.append(g0_lines[-1])  # 只保留最后一个G0
    return result

def process_file(input_path, output_path):
    """处理G-code文件，删除非T0块中的连续G0指令"""
    try:
        with open(input_path, 'r') as file:
            data = file.readlines()

        processed_data = []
        block = []
        for line in data:
            if line.strip() == "":
                # 如果遇到空行，处理当前数据块
                if block:
                    # 检查是否以T0开头，不进行处理
                    if block[0].startswith("T0"):
                        processed_data.extend(block)
                    else:
                        processed_data.extend(remove_continuous_g0(block))
                    processed_data.append("")  # 保留空行分隔数据块
                    block = []  # 重置块
            else:
                block.append(line)

        # 处理最后一个数据块
        if block:
            if block[0].startswith("T0"):
                processed_data.extend(block)
            else:
                processed_data.extend(remove_continuous_g0(block))

        # 写入输出文件
        with open(output_path, 'w') as file:
            file.writelines(processed_data)
        print("G0Trimmer 处理完成！")
    except Exception as e:
        raise Exception(f"处理文件时出错: {e}")