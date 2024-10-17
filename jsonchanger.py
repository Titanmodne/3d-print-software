import json
import tkinter as tk
from tkinter import filedialog

# 创建一个 Tkinter 根窗口并隐藏
root = tk.Tk()
root.withdraw()

# 询问用户选择 JSON 文件
file_path = filedialog.askopenfilename(
    title="选择 JSON 配置文件",
    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
)

if file_path:
    # 读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        config_data = json.load(file)

    config_data['settings']['resolution']['children']['layer_height']['default_value'] = 0.2
    config_data['settings']['resolution']['children']['layer_height_0']['default_value'] = 0.3
    config_data['settings']['resolution']['children']['line_width']['default_value'] = 0.4
    config_data['settings']['resolution']['children']['line_width']['children']['wall_line_width'][
        'default_value'] = 0.5
    config_data['settings']['resolution']['children']['line_width']['children']['wall_line_width']['children'][
        'wall_line_width_0']['default_value'] = 0.6
    config_data['settings']['resolution']['children']['line_width']['children']['wall_line_width']['children'][
        'wall_line_width_x']['default_value'] = 0.7
    config_data['settings']['resolution']['children']['line_width']['children']['infill_line_width'][
        'default_value'] = 0.8
    config_data['settings']['resolution']['children']['initial_layer_line_width_factor'][
        'default_value'] = 0.9
    config_data['settings']['shell']['children']['wall_thickness']['default_value'] = 1.0
    config_data['settings']['shell']['children']['wall_thickness']['children']['wall_line_count']['default_value'] = 10
    config_data['settings']['shell']['children']['optimize_wall_printing_order']['default_value'] = True
    config_data['settings']['shell']['children']['inset_direction']['default_value'] = "inside_out"
    config_data['settings']['shell']['children']['min_wall_line_width']['default_value'] = 0.2
    config_data['settings']['shell']['children']['min_wall_line_width']['children']['min_even_wall_line_width'][
        'default_value'] = 0.25
    config_data['settings']['shell']['children']['min_wall_line_width']['children']['min_odd_wall_line_width'][
        'default_value'] = 0.25
    config_data['settings']['shell']['children']['z_seam_type']['default_value'] = "back"
    config_data['settings']['top_bottom']['children']['top_bottom_thickness']['default_value'] = 1.2
    config_data['settings']['top_bottom']['children']['top_bottom_thickness']['children']['top_thickness']['default_value'] = 0.6
    config_data['settings']['top_bottom']['children']['top_bottom_thickness']['children']['top_thickness']['children']['top_layers']['default_value'] = 6
    config_data['settings']['top_bottom']['children']['top_bottom_thickness']['children']['bottom_thickness']['default_value'] = 0.6
    config_data['settings']['top_bottom']['children']['top_bottom_thickness']['children']['bottom_thickness']['children']['bottom_layers']['default_value'] = 6
    config_data['settings']['top_bottom']['children']['top_bottom_thickness']['children']['bottom_thickness']['children']['initial_bottom_layers']['default_value'] = 2
    config_data['settings']['infill']['children']['infill_sparse_density']['default_value'] = 20
    config_data['settings']['infill']['children']['infill_sparse_density']['children']['infill_line_distance']['default_value'] = 2.0
    config_data['settings']['infill']['children']['infill_pattern']['default_value'] = "grid"
    config_data['settings']['infill']['children']['connect_infill_polygons']['default_value'] = True
    config_data['settings']['infill']['children']['infill_angles']['default_value'] = [45, -45]
    config_data['settings']['infill']['children']['infill_multiplier']['default_value'] = 1
    config_data['settings']['infill']['children']['infill_overlap']['default_value'] = 10
    config_data['settings']['infill']['children']['infill_overlap']['children']['infill_overlap_mm']['default_value'] = 0.1
    config_data['settings']['infill']['children']['infill_wipe_dist']['default_value'] = 0.1
    config_data['settings']['infill']['children']['infill_sparse_thickness']['default_value'] = 0.3

    # 将更新后的数据写回文件
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(config_data, file, indent=4, ensure_ascii=False)

    print("配置文件已更新。")
else:
    print("未选择文件。")
