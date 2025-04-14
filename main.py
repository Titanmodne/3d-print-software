import sys
import json
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
                             QMessageBox, QHBoxLayout, QComboBox, QDoubleSpinBox, QSpinBox, QTabWidget, QLineEdit)
from PyQt5.QtCore import Qt

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
from cutter import process_gcode_file as twelfth_step
from change_f import process_file as thirteenth_step
from upupup import process_file as fourteenth_step
from joffset import process_file as fifteenth_step
from endZup import process_file as sixteenth_step
from add_commands import add_commands_and_swap_T0_T1 as seventeenth_step
from trans_gcode_to_array import process_gcode_to_array as eighteenth_step
from arraytojbi import process_array_to_jbi as nineteenth_step
from offset import process_gcode_with_offset as twentieth_step

# JSON 配置编辑器类
class JsonConfigEditor(QWidget):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        # 参数字典，已移除 "initial_layer_line_width_factor"
        self.parameters = {
            "layer_height": ("层高", "float", ["settings", "resolution", "children", "layer_height", "default_value"], 0.001, 0.8),
            "layer_height_0": ("起始层高", "float", ["settings", "resolution", "children", "layer_height_0", "default_value"], 0.001, 0.8),
            "line_width": ("走线宽度", "float", ["settings", "resolution", "children", "line_width", "default_value"], 0.001, 10),
            "wall_line_width": ("走线宽度(壁)", "float", ["settings", "resolution", "children", "line_width", "children", "wall_line_width", "default_value"], 0.001, 10),
            "wall_line_width_0": ("走线宽度(外壁)", "float", ["settings", "resolution", "children", "line_width", "children", "wall_line_width_0", "default_value"], 0.001, 10),
            "wall_line_width_x": ("走线宽度(内壁)", "float", ["settings", "resolution", "children", "line_width", "children", "wall_line_width_x", "default_value"], 0.001, 10),
            "wall_thickness": ("壁厚", "float", ["settings", "shell", "children", "wall_thickness", "default_value"], 0, 999999),
            "wall_line_count": ("壁走线次数", "int", ["settings", "shell", "children", "wall_thickness", "children", "wall_line_count", "default_value"], 0, 999999),
            "top_bottom_thickness": ("顶层/底层厚度", "float", ["settings", "top_bottom", "children", "top_bottom_thickness", "default_value"], 0.2, 10),
            "top_thickness": ("顶层厚度", "float", ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "top_thickness", "default_value"], 0.2, 10),
            "top_layers": ("顶部层数", "int", ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "top_thickness", "children", "top_layers", "default_value"], 0, 100),
            "bottom_thickness": ("底层厚度", "float", ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "bottom_thickness", "default_value"], 0.2, 10),
            "bottom_layers": ("底部层数", "int", ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "bottom_thickness", "children", "bottom_layers", "default_value"], 0, 100),
            "infill_line_distance": ("填充走线距离", "float", ["settings", "infill", "children", "infill_sparse_density", "children", "infill_line_distance", "default_value"], 0, 10),
            "infill_pattern": ("填充图案", "enum", ["settings", "infill", "children", "infill_pattern", "default_value"], ["grid", "lines", "triangles", "trihexagon", "cubic", "cubicsubdiv"]),
            "infill_sparse_thickness": ("填充层厚度", "float", ["settings", "infill", "children", "infill_sparse_thickness", "default_value"], 0.1, 10)
        }
        self.inputs = {}
        self.json_data = None
        self.file_path = r"C:\Program Files\UltiMaker Cura 5.8.1\share\cura\resources\definitions\fdmprinter.def.json"
        self.initUI()
        self.loadJson()
        if config:
            self.load_config(config)

    def initUI(self):
        layout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        layout.addWidget(self.tabWidget)

        # 分组字典，已从“走线宽度设置”中移除 "initial_layer_line_width_factor"
        groups = {
            "层高设置": ["layer_height", "layer_height_0"],
            "走线宽度设置": ["line_width", "wall_line_width", "wall_line_width_0", "wall_line_width_x"],
            "壁设置": ["wall_thickness", "wall_line_count"],
            "顶层/底层设置": ["top_bottom_thickness", "top_thickness", "top_layers", "bottom_thickness", "bottom_layers"],
            "填充设置": ["infill_line_distance", "infill_pattern", "infill_sparse_thickness"]
        }

        for tab_name, keys in groups.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            for key in keys:
                self.addParameterToLayout(key, tab_layout)
            tab.setLayout(tab_layout)
            self.tabWidget.addTab(tab, tab_name)

        self.btnSave = QPushButton('保存更改', self)
        self.btnSave.clicked.connect(self.saveChanges)
        layout.addWidget(self.btnSave)

        self.btnSaveConfig = QPushButton('保存配置文件', self)
        self.btnSaveConfig.clicked.connect(self.saveFullConfig)
        layout.addWidget(self.btnSaveConfig)

        self.btnLoadConfig = QPushButton('加载配置文件', self)
        self.btnLoadConfig.clicked.connect(self.loadFullConfig)
        layout.addWidget(self.btnLoadConfig)

        self.btnSlice = QPushButton('切片 STL 文件', self)
        self.btnSlice.clicked.connect(self.sliceSTL)
        layout.addWidget(self.btnSlice)

    def addParameterToLayout(self, key, layout):
        param = self.parameters[key]
        label, type_, path, *range_ = param
        row = QHBoxLayout()
        label_widget = QLabel(label + ":")
        label_widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row.addWidget(label_widget, 1)

        if type_ == "float":
            input_widget = QDoubleSpinBox()
            input_widget.setRange(range_[0], range_[1])
            input_widget.setDecimals(3)
        elif type_ == "int":
            input_widget = QSpinBox()
            input_widget.setRange(range_[0], range_[1])
        elif type_ == "bool":
            input_widget = QComboBox()
            input_widget.addItems(["true", "false"])
        elif type_ == "enum":
            input_widget = QComboBox()
            input_widget.addItems(range_[0])

        self.inputs[key] = (input_widget, path)
        row.addWidget(input_widget, 2)
        layout.addLayout(row)

    def loadJson(self):
        try:
            if not self.file_path:
                self.file_path = QFileDialog.getOpenFileName(self, "选择 JSON 文件", "", "JSON Files (*.json);;All Files (*)")[0]
            if not self.file_path:
                return
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.json_data = json.load(file)
            self.populateFields()
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON 文件格式不正确:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载 JSON 文件时发生错误:\n{str(e)}")

    def populateFields(self):
        if self.json_data:
            for key, (widget, path) in self.inputs.items():
                try:
                    value = self.get_value_from_path(path)
                    if value is not None:
                        if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                            widget.setValue(value)
                        elif isinstance(widget, QComboBox) and isinstance(value, bool):
                            widget.setCurrentIndex(widget.findText(str(value).lower()))
                        elif isinstance(widget, QComboBox):
                            widget.setCurrentText(value)
                except Exception as e:
                    print(f"无法加载字段 {key}: {e}")

    def get_value_from_path(self, path):
        data = self.json_data
        for p in path:
            data = data.get(p, None)
            if data is None:
                return None
        return data

    def saveChanges(self):
        if not self.json_data or not self.file_path:
            QMessageBox.warning(self, "错误", "未加载 JSON 文件。")
            return

        for key, (widget, path) in self.inputs.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                value = widget.value()
                formatted_value = value
            elif isinstance(widget, QComboBox):
                if self.parameters[key][1] == "bool":
                    value = widget.currentText() == "true"
                    formatted_value = value
                else:
                    value = widget.currentText()
                    formatted_value = value
            else:
                value = widget.currentText()
                formatted_value = value
            self.set_value_from_path(path, formatted_value)

        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(self.json_data, file, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "成功", "更改已成功保存。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存 JSON 文件时发生错误:\n{str(e)}")

    def set_value_from_path(self, path, value):
        data = self.json_data
        for p in path[:-1]:
            data = data.setdefault(p, {})
        data[path[-1]] = value

    def saveFullConfig(self):
        # 调用 MainApp 的 save_config 方法保存整个程序配置
        main_app = self.window()
        main_app.save_config()

    def loadFullConfig(self):
        # 调用 MainApp 的 load_new_config 方法加载整个程序配置
        main_app = self.window()
        main_app.load_new_config()

    def sliceSTL(self):
        stl_file_path = QFileDialog.getOpenFileName(self, "选择 STL 文件", "", "STL Files (*.stl);;All Files (*)")[0]
        if stl_file_path:
            cura_engine_path = r"C:\Program Files\UltiMaker Cura 5.8.1\CuraEngine.exe"
            config_path = r"C:\Program Files\UltiMaker Cura 5.8.1\share\cura\resources\definitions\fdmprinter.def.json"
            output_path = stl_file_path.replace('.stl', '.gcode')
            try:
                subprocess.run(
                    [cura_engine_path, "slice", "-v", "-j", config_path, "-l", stl_file_path, "-s", "roofing_layer_count=0",
                     "-o", output_path], check=True)
                QMessageBox.information(self, "成功", f"切片完成，输出文件为 {output_path}")
                # 将切片后的 G-code 文件路径传递给 GCodeProcessorApp
                main_app = self.window()
                main_app.gcode_processor_tab.input_path.setText(output_path)
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "切片失败", f"切片过程中发生错误: {str(e)}")

    def load_config(self, config):
        for key, (widget, _) in self.inputs.items():
            if key in config:
                value = config[key]
                if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                    widget.setValue(value)
                elif isinstance(widget, QComboBox) and isinstance(value, bool):
                    widget.setCurrentIndex(widget.findText(str(value).lower()))
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)

    def get_config(self):
        config = {}
        for key, (widget, _) in self.inputs.items():
            if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                config[key] = widget.value()
            elif isinstance(widget, QComboBox):
                if self.parameters[key][1] == "bool":
                    config[key] = widget.currentText() == "true"
                else:
                    config[key] = widget.currentText()
        return config

# G-code 处理类
class GCodeProcessorApp(QWidget):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.default_type_map = {
            'FILL': 'T0',
            'WALL-INNER': 'T1',
            'WALL-OUTER': 'T1',
            'SUPPORT': 'T1',
            'SUPPORT-INTERFACE': 'T1',
            'SKIN': 'T0',
            'SKIRT': 'T0',
        }
        self.initUI()
        if config:
            self.load_config(config)

    def initUI(self):
        layout = QVBoxLayout(self)

        # 输入文件选择
        self.input_label = QLabel("选择输入文件:", self)
        self.input_path = QLineEdit(self)
        self.input_button = QPushButton("浏览", self)
        self.input_button.clicked.connect(self.select_input_file)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(self.input_button)
        layout.addLayout(input_layout)

        # 第十九步输出文件夹选择
        self.nineteenth_output_folder_label = QLabel("选择JBI路径输出文件夹:", self)
        self.nineteenth_output_folder_path = QLineEdit(self)
        self.nineteenth_output_folder_button = QPushButton("浏览", self)
        self.nineteenth_output_folder_button.clicked.connect(self.select_nineteenth_output_folder)

        nineteenth_output_layout = QHBoxLayout()
        nineteenth_output_layout.addWidget(self.nineteenth_output_folder_label)
        nineteenth_output_layout.addWidget(self.nineteenth_output_folder_path)
        nineteenth_output_layout.addWidget(self.nineteenth_output_folder_button)
        layout.addLayout(nineteenth_output_layout)

        # 第十九步参数
        self.user_label = QLabel("USER 值 (默认 2):", self)
        self.user_entry = QLineEdit(self)
        self.user_entry.setText("2")

        self.tool_label = QLabel("TOOL 值 (默认 0):", self)
        self.tool_entry = QLineEdit(self)
        self.tool_entry.setText("0")

        nineteenth_params_layout = QVBoxLayout()
        nineteenth_params_layout.addWidget(self.user_label)
        nineteenth_params_layout.addWidget(self.user_entry)
        nineteenth_params_layout.addWidget(self.tool_label)
        nineteenth_params_layout.addWidget(self.tool_entry)
        layout.addLayout(nineteenth_params_layout)

        # 类型选择下拉框
        self.type_labels = {}
        self.type_combos = {}
        for type_name, default_t in self.default_type_map.items():
            label = QLabel(type_name, self)
            combo = QComboBox(self)
            combo.addItems(["T0", "T1"])
            combo.setCurrentText(default_t)
            self.type_labels[type_name] = label
            self.type_combos[type_name] = combo
            type_layout = QHBoxLayout()
            type_layout.addWidget(label)
            type_layout.addWidget(combo)
            layout.addLayout(type_layout)

        # 第九步偏移量输入
        offset_layout = QHBoxLayout()
        self.offset_x_label = QLabel("X 偏移量 (默认 3.04):", self)
        self.offset_x_entry = QLineEdit(self)
        self.offset_x_entry.setText("3.04")
        self.offset_x_entry.setFixedWidth(80)
        offset_layout.addWidget(self.offset_x_label)
        offset_layout.addWidget(self.offset_x_entry)

        self.offset_y_label = QLabel("Y 偏移量 (默认 -56.471):", self)
        self.offset_y_entry = QLineEdit(self)
        self.offset_y_entry.setText("-56.471")
        self.offset_y_entry.setFixedWidth(80)
        offset_layout.addWidget(self.offset_y_label)
        offset_layout.addWidget(self.offset_y_entry)

        self.offset_z_label = QLabel("Z 偏移量 (默认 -3.11):", self)
        self.offset_z_entry = QLineEdit(self)
        self.offset_z_entry.setText("-3.11")
        self.offset_z_entry.setFixedWidth(80)
        offset_layout.addWidget(self.offset_z_label)
        offset_layout.addWidget(self.offset_z_entry)
        layout.addLayout(offset_layout)

        # 第十一步参数
        self.w_label = QLabel("线宽 W (默认 1.2):", self)
        self.w_entry = QLineEdit(self)
        self.w_entry.setText("1.2")

        self.h_label = QLabel("层厚 H (默认 0.2):", self)
        self.h_entry = QLineEdit(self)
        self.h_entry.setText("0.2")

        self.k2_label = QLabel("连续纤维挤出系数值 (默认 0.98):", self)
        self.k2_entry = QLineEdit(self)
        self.k2_entry.setText("0.98")

        self.f1_label = QLabel("F1 进给速度 (默认 1000):", self)
        self.f1_entry = QLineEdit(self)
        self.f1_entry.setText("1000")

        self.f2_label = QLabel("F2 进给速度 (默认 500):", self)
        self.f2_entry = QLineEdit(self)
        self.f2_entry.setText("500")

        eleventh_step_params_layout = QVBoxLayout()
        eleventh_step_params_layout.addWidget(self.w_label)
        eleventh_step_params_layout.addWidget(self.w_entry)
        eleventh_step_params_layout.addWidget(self.h_label)
        eleventh_step_params_layout.addWidget(self.h_entry)
        eleventh_step_params_layout.addWidget(self.k2_label)
        eleventh_step_params_layout.addWidget(self.k2_entry)
        eleventh_step_params_layout.addWidget(self.f1_label)
        eleventh_step_params_layout.addWidget(self.f1_entry)
        eleventh_step_params_layout.addWidget(self.f2_label)
        eleventh_step_params_layout.addWidget(self.f2_entry)
        layout.addLayout(eleventh_step_params_layout)

        # 第十二步参数
        self.distance_label = QLabel("剪断距离 (mm):", self)
        self.distance_entry = QLineEdit(self)
        self.distance_entry.setText("5.0")

        self.insert_f_label = QLabel("初始移动速度:", self)
        self.insert_f_entry = QLineEdit(self)
        self.insert_f_entry.setText("300")

        self.connection_f_label = QLabel("跳转F值:", self)
        self.connection_f_entry = QLineEdit(self)
        self.connection_f_entry.setText("800")

        self.j_distance_label = QLabel("预挤出长度 J_distance:", self)
        self.j_distance_entry = QLineEdit(self)
        self.j_distance_entry.setText("10.0")

        twelfth_step_params_layout = QVBoxLayout()
        twelfth_step_params_layout.addWidget(self.distance_label)
        twelfth_step_params_layout.addWidget(self.distance_entry)
        twelfth_step_params_layout.addWidget(self.insert_f_label)
        twelfth_step_params_layout.addWidget(self.insert_f_entry)
        twelfth_step_params_layout.addWidget(self.connection_f_label)
        twelfth_step_params_layout.addWidget(self.connection_f_entry)
        twelfth_step_params_layout.addWidget(self.j_distance_label)
        twelfth_step_params_layout.addWidget(self.j_distance_entry)
        layout.addLayout(twelfth_step_params_layout)

        # 第二十步全局偏移坐标
        twentieth_step_params_layout = QHBoxLayout()
        self.global_offset_x_label = QLabel("整体偏置 X:", self)
        self.global_offset_x_entry = QLineEdit(self)
        self.global_offset_x_entry.setText("100.0")
        self.global_offset_x_entry.setFixedWidth(80)
        twentieth_step_params_layout.addWidget(self.global_offset_x_label)
        twentieth_step_params_layout.addWidget(self.global_offset_x_entry)

        self.global_offset_y_label = QLabel("整体偏置 Y:", self)
        self.global_offset_y_entry = QLineEdit(self)
        self.global_offset_y_entry.setText("200.0")
        self.global_offset_y_entry.setFixedWidth(80)
        twentieth_step_params_layout.addWidget(self.global_offset_y_label)
        twentieth_step_params_layout.addWidget(self.global_offset_y_entry)

        self.global_offset_z_label = QLabel("整体偏置 Z:", self)
        self.global_offset_z_entry = QLineEdit(self)
        self.global_offset_z_entry.setText("0.0")
        self.global_offset_z_entry.setFixedWidth(80)
        twentieth_step_params_layout.addWidget(self.global_offset_z_label)
        twentieth_step_params_layout.addWidget(self.global_offset_z_entry)
        layout.addLayout(twentieth_step_params_layout)

        # 处理按钮
        self.process_button = QPushButton("开始处理", self)
        self.process_button.clicked.connect(self.process_files)
        layout.addWidget(self.process_button)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择输入文件", "", "G-code files (*.gcode)")
        if file_path:
            self.input_path.setText(file_path)

    def select_nineteenth_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择路径输出文件夹")
        if folder_path:
            self.nineteenth_output_folder_path.setText(folder_path)

    def process_files(self):
        input_file = self.input_path.text()
        nineteenth_output_folder = self.nineteenth_output_folder_path.text()

        if not input_file:
            QMessageBox.warning(self, "错误", "请选择输入文件")
            return
        if not nineteenth_output_folder:
            QMessageBox.warning(self, "错误", "请选择路径输出文件夹")
            return

        try:
            user = int(self.user_entry.text())
            tool = int(self.tool_entry.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的 用户坐标系 和 工具坐标系 值（整数）")
            return

        type_map = {type_name: combo.currentText() for type_name, combo in self.type_combos.items()}

        try:
            offset_x = float(self.offset_x_entry.text())
            offset_y = float(self.offset_y_entry.text())
            offset_z = float(self.offset_z_entry.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的 ninth_step 偏移量（数字）")
            return

        try:
            w = float(self.w_entry.text())
            h = float(self.h_entry.text())
            k2 = float(self.k2_entry.text())
            f1 = float(self.f1_entry.text())
            f2 = float(self.f2_entry.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的第十一步参数（数字）")
            return

        try:
            distance = float(self.distance_entry.text())
            insert_f = float(self.insert_f_entry.text())
            connection_f = float(self.connection_f_entry.text())
            j_distance = float(self.j_distance_entry.text())
            j_offset = j_distance - distance
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的第十二步参数（数字）")
            return

        try:
            global_offset_x = float(self.global_offset_x_entry.text())
            global_offset_y = float(self.global_offset_y_entry.text())
            global_offset_z = float(self.global_offset_z_entry.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的整体偏置坐标（数字）")
            return

        try:
            intermediate_output1 = "intermediate_1.gcode"
            intermediate_output2 = "intermediate_2.gcode"
            intermediate_output3 = "intermediate_3.gcode"
            intermediate_output4 = "intermediate_4.gcode"
            intermediate_output5 = "intermediate_5.gcode"
            intermediate_output6 = "intermediate_6.gcode"
            intermediate_output7 = "intermediate_7.gcode"
            intermediate_output8 = "intermediate_8.gcode"
            intermediate_output_zreorganize = "intermediate_zreorganize.gcode"
            intermediate_output9 = "intermediate_9.gcode"
            intermediate_output10 = "intermediate_10.gcode"
            eleventh_output = "intermediate_11.gcode"
            twelfth_output = "intermediate_12.gcode"
            thirteenth_output = "intermediate_13.gcode"
            fourteenth_output = "intermediate_14.gcode"
            fifteenth_output = "intermediate_15.gcode"
            intermediate_16 = "intermediate_16.gcode"
            intermediate_17 = "intermediate_17.gcode"
            intermediate_20 = "intermediate_20.gcode"
            intermediate_18 = "intermediate_18.gcode"

            reorganize(input_file, intermediate_output1, type_map)
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
            twelfth_step(eleventh_output, twelfth_output, distance, insert_f, connection_f, j_offset)
            thirteenth_step(twelfth_output, thirteenth_output, insert_f)
            fourteenth_step(thirteenth_output, fourteenth_output)
            fifteenth_step(fourteenth_output, fifteenth_output, -5, -5, j_distance)
            sixteenth_step(fifteenth_output, intermediate_16)
            seventeenth_step(intermediate_16, intermediate_17)
            twentieth_step(intermediate_17, intermediate_20, global_offset_x, global_offset_y, global_offset_z)
            eighteenth_step(intermediate_20, intermediate_18)
            nineteenth_step(intermediate_18, nineteenth_output_folder, user, tool)

            QMessageBox.information(self, "成功", f"所有处理步骤完成！第19步输出文件夹: {nineteenth_output_folder}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理失败: {str(e)}")

    def load_config(self, config):
        if "type_map" in config:
            for type_name, value in config["type_map"].items():
                if type_name in self.type_combos:
                    self.type_combos[type_name].setCurrentText(value)
        self.offset_x_entry.setText(str(config.get("offset_x", 3.04)))
        self.offset_y_entry.setText(str(config.get("offset_y", -56.471)))
        self.offset_z_entry.setText(str(config.get("offset_z", -3.11)))
        self.w_entry.setText(str(config.get("w", 1.2)))
        self.h_entry.setText(str(config.get("h", 0.2)))
        self.k2_entry.setText(str(config.get("k2", 0.98)))
        self.f1_entry.setText(str(config.get("f1", 1000.0)))
        self.f2_entry.setText(str(config.get("f2", 500.0)))
        self.distance_entry.setText(str(config.get("distance", 5.0)))
        self.insert_f_entry.setText(str(config.get("insert_f", 300.0)))
        self.connection_f_entry.setText(str(config.get("connection_f", 800.0)))
        self.j_distance_entry.setText(str(config.get("j_distance", 10.0)))
        self.global_offset_x_entry.setText(str(config.get("global_offset_x", 100.0)))
        self.global_offset_y_entry.setText(str(config.get("global_offset_y", 200.0)))
        self.global_offset_z_entry.setText(str(config.get("global_offset_z", 0.0)))
        self.user_entry.setText(str(config.get("user", 2)))
        self.tool_entry.setText(str(config.get("tool", 0)))
        self.nineteenth_output_folder_path.setText(config.get("nineteenth_output_folder", ""))

    def get_config(self):
        config = {
            "type_map": {type_name: combo.currentText() for type_name, combo in self.type_combos.items()},
            "offset_x": float(self.offset_x_entry.text()),
            "offset_y": float(self.offset_y_entry.text()),
            "offset_z": float(self.offset_z_entry.text()),
            "w": float(self.w_entry.text()),
            "h": float(self.h_entry.text()),
            "k2": float(self.k2_entry.text()),
            "f1": float(self.f1_entry.text()),
            "f2": float(self.f2_entry.text()),
            "distance": float(self.distance_entry.text()),
            "insert_f": float(self.insert_f_entry.text()),
            "connection_f": float(self.connection_f_entry.text()),
            "j_distance": float(self.j_distance_entry.text()),
            "global_offset_x": float(self.global_offset_x_entry.text()),
            "global_offset_y": float(self.global_offset_y_entry.text()),
            "global_offset_z": float(self.global_offset_z_entry.text()),
            "user": int(self.user_entry.text()),
            "tool": int(self.tool_entry.text()),
            "nineteenth_output_folder": self.nineteenth_output_folder_path.text()
        }
        return config

# 主应用程序类
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("集成应用程序")
        self.setGeometry(100, 100, 800, 600)

        # 默认配置文件路径
        self.config_file = "default_config.json"
        self.config_data = self.load_config(self.config_file)

        # 创建 QTabWidget
        self.tabWidget = QTabWidget(self)
        self.setCentralWidget(self.tabWidget)

        # 添加 JSON 配置编辑器选项卡
        self.json_editor_tab = JsonConfigEditor(self, self.config_data.get("json_config", {}))
        self.tabWidget.addTab(self.json_editor_tab, "JSON 配置编辑")

        # 添加 G-code 处理选项卡
        self.gcode_processor_tab = GCodeProcessorApp(self, self.config_data.get("gcode_processor", {}))
        self.tabWidget.addTab(self.gcode_processor_tab, "G-code 文件处理")

        # 添加保存和加载配置的按钮
        self.add_config_buttons()

    def add_config_buttons(self):
        layout = QHBoxLayout()
        self.save_config_btn = QPushButton("保存配置", self)
        self.save_config_btn.clicked.connect(self.save_config)
        layout.addWidget(self.save_config_btn)

        self.load_config_btn = QPushButton("加载配置", self)
        self.load_config_btn.clicked.connect(self.load_new_config)
        layout.addWidget(self.load_config_btn)

        self.tabWidget.setCornerWidget(QWidget())
        self.tabWidget.cornerWidget().setLayout(layout)

    def load_config(self, file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载配置文件失败: {str(e)}")
        # 如果文件不存在，返回默认配置
        return {
            "json_config": {},
            "gcode_processor": {}
        }

    def save_config(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "保存配置文件", "", "JSON Files (*.json)")
        if file_path:
            config = {
                "json_config": self.json_editor_tab.get_config(),
                "gcode_processor": self.gcode_processor_tab.get_config()
            }
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "成功", f"配置文件已保存至: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存配置文件失败: {str(e)}")

    def load_new_config(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载配置文件", "", "JSON Files (*.json)")
        if file_path:
            self.config_data = self.load_config(file_path)
            self.json_editor_tab.load_config(self.config_data.get("json_config", {}))
            self.gcode_processor_tab.load_config(self.config_data.get("gcode_processor", {}))
            QMessageBox.information(self, "成功", f"已加载配置文件: {file_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())