import json
import os
import subprocess
import argparse

# 假设这些模块是你已有的 G-code 处理函数
from reorganization import process_file as reorganize
from TransferG0 import process_file as transfer_g0
from G0Trimmer import process_file as trim_g0
from GCodeAnnotator import process_gcode as next_step
from GCodeProcessor import process_gcode as fifth_step
from GCodeMotionExtractor import process_gcode as sixth_step
from gcodefile import process_gcode as seventh_step
from GCodeZFilter import process_gcode as eighth_step
from Zreorganize import process_z_values as zreorganize_step
from gcodeoffset import process_gcode as ninth_step
from deleteG0 import process_file as tenth_step
from addextrusion import process_jcount as eleventh_step
from beforecheck import process_gcode_file as before_check_step  # 新增的第11.5步
from cutter import process_gcode_file as twelfth_step
from change_f import process_file as thirteenth_step
from upupup import process_file as fourteenth_step
from joffset import process_file as fifteenth_step
from endZup import process_file as sixteenth_step
from add_commands import add_commands_and_swap_T0_T1 as seventeenth_step
from trans_gcode_to_array import process_gcode_to_array as eighteenth_step
from arraytojbi import process_array_to_jbi as nineteenth_step
from offset import process_gcode_with_offset as twentieth_step

def update_json_config(file_path, json_config):
    """直接根据输入的 json_config 更新 fdmprinter.def.json 中的参数值"""
    try:
        if not os.access(file_path, os.W_OK):
            raise PermissionError(f"文件 {file_path} 无写权限，请以管理员权限运行程序")

        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print(f"成功读取 {file_path}")

        print(f"输入的 json_config: {json_config}")

        parameter_paths = {
            "layer_height": ["settings", "resolution", "children", "layer_height", "default_value"],
            "layer_height_0": ["settings", "resolution", "children", "layer_height_0", "default_value"],
            "line_width": ["settings", "resolution", "children", "line_width", "default_value"],
            "wall_line_width": ["settings", "resolution", "children", "line_width", "children", "wall_line_width", "default_value"],
            "wall_line_width_0": ["settings", "resolution", "children", "line_width", "children", "wall_line_width", "children", "wall_line_width_0", "default_value"],
            "wall_line_width_x": ["settings", "resolution", "children", "line_width", "children", "wall_line_width", "children", "wall_line_width_x", "default_value"],
            "infill_line_distance": ["settings", "infill", "children", "infill_sparse_density", "children", "infill_line_distance", "default_value"],
            "top_bottom_thickness": ["settings", "top_bottom", "children", "top_bottom_thickness", "default_value"],
            "top_thickness": ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "top_thickness", "default_value"],
            "top_layers": ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "top_thickness", "children", "top_layers", "default_value"],
            "bottom_thickness": ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "bottom_thickness", "default_value"],
            "bottom_layers": ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "bottom_thickness", "children", "bottom_layers", "default_value"],
            "wall_line_count": ["settings", "shell", "children", "wall_thickness", "children", "wall_line_count", "default_value"],
            "infill_sparse_thickness": ["settings", "infill", "children", "infill_sparse_thickness", "default_value"],
            "infill_pattern": ["settings", "infill", "children", "infill_pattern", "default_value"],
            "initial_bottom_layers": ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "bottom_thickness", "children", "bottom_layers", "default_value"],
            "support_enable": ["settings", "support", "children", "support_enable", "default_value"]
        }

        for param_name, value in json_config.items():
            if param_name in parameter_paths:
                path = parameter_paths[param_name]
                current = json_data
                try:
                    for key in path[:-1]:
                        current = current.setdefault(key, {})
                    current[path[-1]] = value
                    print(f"成功更新 {param_name} 为 {value}")
                except KeyError as e:
                    print(f"更新 {param_name} 失败: 路径 {path} 中缺少键 {e}")
            else:
                print(f"警告: 参数 {param_name} 未在 fdmprinter.def.json 中定义，跳过更新")

        if "bottom_layers" in json_config and "initial_bottom_layers" not in json_config:
            json_config["initial_bottom_layers"] = json_config["bottom_layers"]
            path = parameter_paths["initial_bottom_layers"]
            current = json_data
            try:
                for key in path[:-1]:
                    current = current.setdefault(key, {})
                current[path[-1]] = json_config["bottom_layers"]
                print(f"同步更新 initial_bottom_layers 为 {json_config['bottom_layers']}")
            except KeyError as e:
                print(f"更新 initial_bottom_layers 失败: 路径 {path} 中缺少键 {e}")

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        print(f"成功保存 {file_path}")

    except PermissionError as e:
        print(f"权限错误: {str(e)}")
        raise
    except Exception as e:
        print(f"更新 JSON 文件失败: {str(e)}")
        raise

def sliceSTL(stl_file_path, output_folder, config_data):
    """切片 STL 文件并将生成的 G-code 文件保存到输出文件夹"""
    cura_engine_path = r"C:\Program Files\UltiMaker Cura 5.8.1\CuraEngine.exe"
    config_path = r"C:\Program Files\UltiMaker Cura 5.8.1\share\cura\resources\definitions\fdmprinter.def.json"
    output_path = os.path.join(output_folder, os.path.basename(stl_file_path).replace('.stl', '.gcode'))

    try:
        json_config = config_data.get("json_config", {})
        if not json_config:
            raise ValueError("配置文件中缺少 json_config 部分")
        update_json_config(config_path, json_config)

        result = subprocess.run(
            [cura_engine_path, "slice", "-v", "-j", config_path, "-l", stl_file_path,
             "-s", "roofing_layer_count=0", "-o", output_path],
            check=True, capture_output=True, text=True)
        print(f"CuraEngine output: {result.stdout}")
        print(f"切片完成，输出文件为 {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"切片失败: {str(e)}")
        print(f"Error output: {e.output}")
        return None
    except Exception as e:
        print(f"切片过程中发生错误: {str(e)}")
        return None

def process_files(input_gcode_path, output_folder, config_data):
    """处理 G-code 文件，执行 20 个步骤，所有中间文件保存在输出文件夹"""
    gcode_processor = config_data.get("gcode_processor", {})
    required_params = [
        "type_map", "offset_x", "offset_y", "offset_z", "w", "h", "k2", "f1", "f2",
        "distance", "insert_f", "connection_f", "j_distance", "global_offset_x",
        "global_offset_y", "global_offset_z", "user", "tool"
    ]
    missing_params = [param for param in required_params if param not in gcode_processor]
    if missing_params:
        raise ValueError(f"配置文件缺少必需参数: {', '.join(missing_params)}")

    type_map = gcode_processor["type_map"]
    offset_x = gcode_processor["offset_x"]
    offset_y = gcode_processor["offset_y"]
    offset_z = gcode_processor["offset_z"]
    w = gcode_processor["w"]
    h = gcode_processor["h"]
    k2 = gcode_processor["k2"]
    f1 = gcode_processor["f1"]
    f2 = gcode_processor["f2"]
    distance = gcode_processor["distance"]
    insert_f = gcode_processor["insert_f"]
    connection_f = gcode_processor["connection_f"]
    j_distance = gcode_processor["j_distance"]
    global_offset_x = gcode_processor["global_offset_x"]
    global_offset_y = gcode_processor["global_offset_y"]
    global_offset_z = gcode_processor["global_offset_z"]
    user = gcode_processor["user"]
    tool = gcode_processor["tool"]

    try:
        intermediate_output1 = os.path.join(output_folder, "intermediate_1.gcode")
        intermediate_output2 = os.path.join(output_folder, "intermediate_2.gcode")
        intermediate_output3 = os.path.join(output_folder, "intermediate_3.gcode")
        intermediate_output4 = os.path.join(output_folder, "intermediate_4.gcode")
        intermediate_output5 = os.path.join(output_folder, "intermediate_5.gcode")
        intermediate_output6 = os.path.join(output_folder, "intermediate_6.gcode")
        intermediate_output7 = os.path.join(output_folder, "intermediate_7.gcode")
        intermediate_output8 = os.path.join(output_folder, "intermediate_8.gcode")
        intermediate_output_zreorganize = os.path.join(output_folder, "intermediate_zreorganize.gcode")
        intermediate_output9 = os.path.join(output_folder, "intermediate_9.gcode")
        intermediate_output10 = os.path.join(output_folder, "intermediate_10.gcode")
        eleventh_output = os.path.join(output_folder, "intermediate_11.gcode")
        before_check_output = os.path.join(output_folder, "intermediate_11_5.gcode")  # 新增中间文件
        twelfth_output = os.path.join(output_folder, "intermediate_12.gcode")
        thirteenth_output = os.path.join(output_folder, "intermediate_13.gcode")
        fourteenth_output = os.path.join(output_folder, "intermediate_14.gcode")
        fifteenth_output = os.path.join(output_folder, "intermediate_15.gcode")
        intermediate_16 = os.path.join(output_folder, "intermediate_16.gcode")
        intermediate_17 = os.path.join(output_folder, "intermediate_17.gcode")
        intermediate_20 = os.path.join(output_folder, "intermediate_20.gcode")
        intermediate_18 = os.path.join(output_folder, "intermediate_18.gcode")

        reorganize(input_gcode_path, intermediate_output1, type_map)
        transfer_g0(intermediate_output1, intermediate_output2)
        trim_g0(intermediate_output2, intermediate_output3)
        next_step(intermediate_output3, intermediate_output4)
        fifth_step(intermediate_output4, intermediate_output5)
        sixth_step(intermediate_output5, intermediate_output6)
        seventh_step(intermediate_output6, intermediate_output7)
        eighth_step(intermediate_output7, intermediate_output8)
        zreorganize_step(intermediate_output8, intermediate_output_zreorganize)
        ninth_step(intermediate_output_zreorganize, intermediate_output9, offset_x, offset_y, offset_z)
        tenth_step(intermediate_output9, intermediate_output10)
        eleventh_step(intermediate_output10, eleventh_output, w, h, k2, f1, f2)
        before_check_step(eleventh_output, before_check_output)  # 新增第11.5步
        twelfth_step(before_check_output, twelfth_output, distance, insert_f, connection_f, j_distance - distance)
        thirteenth_step(twelfth_output, thirteenth_output, insert_f)
        fourteenth_step(thirteenth_output, fourteenth_output)
        fifteenth_step(fourteenth_output, fifteenth_output, -5, -5, j_distance)
        sixteenth_step(fifteenth_output, intermediate_16)
        seventeenth_step(intermediate_16, intermediate_17)
        twentieth_step(intermediate_17, intermediate_20, global_offset_x, global_offset_y, global_offset_z)
        eighteenth_step(intermediate_20, intermediate_18)
        nineteenth_step(intermediate_18, output_folder, user, tool)

        print(f"所有处理步骤完成！第19步输出文件夹: {output_folder}")

    except Exception as e:
        print(f"处理失败: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="STL 文件切片和 G-code 处理工具")
    parser.add_argument("stl_file", help="STL 文件路径")
    parser.add_argument("output_folder", help="输出文件夹路径")
    parser.add_argument("--config", help="配置文件路径", default=os.path.join(os.getcwd(), '1231.json'))
    args = parser.parse_args()

    if not os.path.exists(args.output_folder):
        os.makedirs(args.output_folder)

    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"错误: 加载配置文件失败: {str(e)}")
        return

    gcode_file = sliceSTL(args.stl_file, args.output_folder, config_data)
    if gcode_file:
        process_files(gcode_file, args.output_folder, config_data)

if __name__ == "__main__":
    main()