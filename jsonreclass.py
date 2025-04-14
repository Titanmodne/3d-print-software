import json

def classify_json(input_file, output_file):
    """
    从输入的 JSON 文件中读取数据，进行分类处理，并将分类后的数据写入到输出 JSON 文件中。

    参数:
        input_file (str): 输入 JSON 文件的路径
        output_file (str): 输出 JSON 文件的路径
    """
    # 预定义的分类规则
    json_config_keys = [
        "bottom_layers",
        "top_layers",
        "wall_loops",
        "print_spacing",
        "infill_pattern",
        "enable_support"  # 添加 enable_support 到 json_config_keys
    ]
    gcode_processor_keys = [
        "infill_extruder",
        "inner_wall_extruder",
        "outer_wall_extruder",
        "support_extruder",
        "surface_support_extruder",
        "skin_extruder",
        "skirt_extruder",
        "extrusion_rate",
        "normal_speed",
        "initial_speed",
        "lift_speed",
        "print_speed",
        "multi_start_point",
        "multi_t0_to_t1",
        "multi_cut_length",
        "multi_pre_feed_length",
        "user_coordinate_value",
        "tool_coordinate_value"
    ]

    try:
        # 读取输入 JSON 文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 初始化分类字典
        classified = {
            "json_config": {},
            "gcode_processor": {},
            "待分类": {}
        }

        # 特殊处理 layer_thickness 和 line_width
        if "layer_thickness" in data:
            classified["json_config"]["layer_thickness"] = data["layer_thickness"]
            classified["gcode_processor"]["layer_thickness"] = data["layer_thickness"]
        if "line_width" in data:
            classified["json_config"]["line_width"] = data["line_width"]
            classified["gcode_processor"]["line_width"] = data["line_width"]

        # 遍历 JSON 数据的主层级
        for key, value in data.items():
            if key in json_config_keys:
                classified["json_config"][key] = value
            elif key in gcode_processor_keys:
                classified["gcode_processor"][key] = value
            elif key not in ["layer_thickness", "line_width"]:
                classified["待分类"][key] = value

        # 处理嵌套的 material_settings
        if "material_settings" in data:
            classified["待分类"]["material_settings"] = {}
            for sub_key, sub_value in data["material_settings"].items():
                if sub_key in gcode_processor_keys:
                    classified["gcode_processor"][sub_key] = sub_value
                else:
                    classified["待分类"]["material_settings"][sub_key] = sub_value

        # 处理嵌套的 device_settings
        if "device_settings" in data:
            classified["待分类"]["device_settings"] = {}
            for sub_key, sub_value in data["device_settings"].items():
                if sub_key in gcode_processor_keys:
                    classified["gcode_processor"][sub_key] = sub_value
                else:
                    classified["待分类"]["device_settings"][sub_key] = sub_value

        # 将分类后的数据写入输出 JSON 文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(classified, f, indent=4, ensure_ascii=False)
        print(f"分类完成，结果已保存到 {output_file}")

    except FileNotFoundError:
        print(f"错误: 文件 {input_file} 不存在。")
    except json.JSONDecodeError:
        print(f"错误: 文件 {input_file} 不是有效的 JSON 格式。")
    except Exception as e:
        print(f"发生错误: {str(e)}")

# 示例用法
if __name__ == "__main__":
    input_file = "config.json"  # 输入 JSON 文件
    output_file = "classified_config.json"  # 输出 JSON 文件
    classify_json(input_file, output_file)