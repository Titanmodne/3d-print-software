import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
                             QMessageBox, QHBoxLayout, QComboBox, QDoubleSpinBox, QSpinBox, QLineEdit)
from PyQt5.QtCore import Qt

# 假设这些导入的模块是你程序中已有的 G-code 处理函数
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

        self.input_label = QLabel("选择输入文件:", self)
        self.input_path = QLineEdit(self)
        self.input_button = QPushButton("浏览", self)
        self.input_button.clicked.connect(self.select_input_file)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(self.input_button)
        layout.addLayout(input_layout)

        self.nineteenth_output_folder_label = QLabel("选择JBI路径输出文件夹:", self)
        self.nineteenth_output_folder_path = QLineEdit(self)
        self.nineteenth_output_folder_button = QPushButton("浏览", self)
        self.nineteenth_output_folder_button.clicked.connect(self.select_nineteenth_output_folder)
        nineteenth_output_layout = QHBoxLayout()
        nineteenth_output_layout.addWidget(self.nineteenth_output_folder_label)
        nineteenth_output_layout.addWidget(self.nineteenth_output_folder_path)
        nineteenth_output_layout.addWidget(self.nineteenth_output_folder_button)
        layout.addLayout(nineteenth_output_layout)

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

class GCodeProcessorAppMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-code 文件处理")
        self.setGeometry(100, 100, 800, 600)
        self.config_file = "gcode_processor_config.json"
        self.config_data = self.load_config()

        self.gcode_processor = GCodeProcessorApp(self, self.config_data.get("gcode_processor", {}))

        # 创建加载和保存按钮
        self.load_config_button = QPushButton("加载配置文件", self)
        self.save_config_button = QPushButton("保存配置文件", self)

        # 连接槽函数
        self.load_config_button.clicked.connect(self.load_new_config)
        self.save_config_button.clicked.connect(self.save_config)

        # 创建主布局
        layout = QVBoxLayout()
        layout.addWidget(self.load_config_button)
        layout.addWidget(self.save_config_button)
        layout.addWidget(self.gcode_processor)

        # 设置中心部件
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_config(self):
        """加载默认配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载配置文件失败: {str(e)}")
        return {"gcode_processor": {}}

    def save_config(self):
        """保存配置文件"""
        config = {"gcode_processor": self.gcode_processor.get_config()}
        file_path, _ = QFileDialog.getSaveFileName(self, "保存配置文件", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                QMessageBox.information(self, "成功", f"配置文件已保存至: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存配置文件失败: {str(e)}")

    def load_new_config(self):
        """加载用户选择的配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "加载配置文件", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.gcode_processor.load_config(config.get("gcode_processor", {}))
                QMessageBox.information(self, "成功", f"已加载配置文件: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载配置文件失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    processor_app = GCodeProcessorAppMain()
    processor_app.show()
    sys.exit(app.exec_())