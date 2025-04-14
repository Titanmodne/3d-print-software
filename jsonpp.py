import json

def map_parameters(input_data):
    # 初始化输出结构
    output_data = {
        "version": "1.0",
        "json_config": {},
        "gcode_processor": {}
    }

    # --- json_config 部分 ---
    layer_thickness = float(input_data["json_config"]["layer_thickness"])
    output_data["json_config"]["layer_height"] = layer_thickness
    output_data["json_config"]["layer_height_0"] = layer_thickness
    output_data["json_config"]["top_bottom_thickness"] = layer_thickness
    output_data["json_config"]["bottom_thickness"] = layer_thickness
    output_data["json_config"]["infill_sparse_thickness"] = layer_thickness

    line_width = float(input_data["json_config"]["line_width"])
    output_data["json_config"]["line_width"] = line_width
    output_data["json_config"]["wall_line_width"] = line_width
    output_data["json_config"]["wall_line_width_0"] = line_width
    output_data["json_config"]["wall_line_width_x"] = line_width
    output_data["json_config"]["infill_line_distance"] = line_width

    output_data["json_config"]["bottom_layers"] = int(input_data["json_config"]["bottom_layers"])
    output_data["json_config"]["top_layers"] = int(input_data["json_config"]["top_layers"])
    output_data["json_config"]["wall_line_count"] = int(input_data["json_config"]["wall_loops"])
    output_data["json_config"]["infill_pattern"] = input_data["json_config"]["infill_pattern"]

    # 添加 enable_support 的映射
    if "enable_support" in input_data["json_config"]:
        output_data["json_config"]["support_enable"] = input_data["json_config"]["enable_support"]

    # --- gcode_processor 部分 ---
    output_data["gcode_processor"]["h"] = float(input_data["gcode_processor"]["layer_thickness"])
    output_data["gcode_processor"]["w"] = float(input_data["gcode_processor"]["line_width"])

    output_data["gcode_processor"]["type_map"] = {
        "FILL": input_data["gcode_processor"]["infill_extruder"],
        "WALL-INNER": input_data["gcode_processor"]["inner_wall_extruder"],
        "WALL-OUTER": input_data["gcode_processor"]["outer_wall_extruder"],
        "SUPPORT": input_data["gcode_processor"]["support_extruder"],
        "SUPPORT-INTERFACE": input_data["gcode_processor"]["surface_support_extruder"],
        "SKIN": input_data["gcode_processor"]["skin_extruder"],
        "SKIRT": input_data["gcode_processor"]["skirt_extruder"]
    }

    output_data["gcode_processor"]["k2"] = float(input_data["gcode_processor"]["extrusion_rate"])
    output_data["gcode_processor"]["f2"] = float(input_data["gcode_processor"]["normal_speed"])
    output_data["gcode_processor"]["insert_f"] = float(input_data["gcode_processor"]["initial_speed"])
    output_data["gcode_processor"]["connection_f"] = float(input_data["gcode_processor"]["lift_speed"])
    output_data["gcode_processor"]["f1"] = float(input_data["gcode_processor"]["print_speed"])
    output_data["gcode_processor"]["distance"] = float(input_data["gcode_processor"]["multi_cut_length"])
    output_data["gcode_processor"]["j_distance"] = float(input_data["gcode_processor"]["multi_pre_feed_length"])
    output_data["gcode_processor"]["user"] = int(input_data["gcode_processor"]["user_coordinate_value"])
    output_data["gcode_processor"]["tool"] = int(input_data["gcode_processor"]["tool_coordinate_value"])

    multi_start_point = input_data["gcode_processor"]["multi_start_point"]
    output_data["gcode_processor"]["global_offset_x"] = float(multi_start_point["x"])
    output_data["gcode_processor"]["global_offset_y"] = float(multi_start_point["y"])
    output_data["gcode_processor"]["global_offset_z"] = float(multi_start_point["z"])

    multi_t0_to_t1 = input_data["gcode_processor"]["multi_t0_to_t1"]
    output_data["gcode_processor"]["offset_x"] = float(multi_t0_to_t1["x"])
    output_data["gcode_processor"]["offset_y"] = float(multi_t0_to_t1["y"])
    output_data["gcode_processor"]["offset_z"] = float(multi_t0_to_t1["z"])

    output_data["gcode_processor"]["nineteenth_output_folder"] = ""

    # 直接返回 output_data，保留 version
    return output_data