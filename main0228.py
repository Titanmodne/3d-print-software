import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
from reorganization import process_file as reorganize  # 第一步
from TransferG0 import process_file as transfer_g0     # 第二步
from G0Trimmer import process_file as trim_g0          # 第三步
from GCodeAnnotator import process_gcode as next_step  # 第四步
from GCodeProcessor import process_gcode as fifth_step # 第五步
from GCodeMotionExtractor import process_gcode as sixth_step  # 第六步
from gcodefile import process_gcode as seventh_step    # 第七步
from GCodeZFilter import process_gcode as eighth_step  # 第八步
from Zreorganize import process_z_values as zreorganize_step  # Zreorganize 步骤
from gcodeoffset import process_gcode as ninth_step    # 第九步
from deleteG0 import process_file as tenth_step        # 第十步
from addextrusion import process_jcount as eleventh_step  # 第十一步
from cutter import process_gcode_file as twelfth_step  # 第十二步
from change_f import process_file as thirteenth_step  # 第十三步
from upupup import process_file as fourteenth_step    # 第十四步
from joffset import process_file as fifteenth_step     # 第十五步
from endZup import process_file as sixteenth_step      # 第十六步
from add_commands import add_commands_and_swap_T0_T1 as seventeenth_step  # 第十七步
from trans_gcode_to_array import process_gcode_to_array as eighteenth_step  # 第十八步
from arraytojbi import process_array_to_jbi as nineteenth_step  # 第十九步
from offset import process_gcode_with_offset as twentieth_step  # 第二十步（从 offset 脚本导入）

class GCodeProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """初始化用户界面"""
        self.setWindowTitle("G-code 文件处理")
        self.setGeometry(100, 100, 600, 700)

        # 默认类型映射
        self.default_type_map = {
            'FILL': 'T0',
            'WALL-INNER': 'T1',
            'WALL-OUTER': 'T1',
            'SUPPORT': 'T1',
            'SUPPORT-INTERFACE': 'T1',
            'SKIN': 'T0',
            'SKIRT': 'T0',
        }

        # 输入文件选择
        self.input_label = QLabel("选择输入文件:")
        self.input_path = QLineEdit()
        self.input_button = QPushButton("浏览")
        self.input_button.clicked.connect(self.select_input_file)

        # 第19步输出文件夹选择
        self.nineteenth_output_folder_label = QLabel("选择JBI路径输出文件夹:")
        self.nineteenth_output_folder_path = QLineEdit()
        self.nineteenth_output_folder_button = QPushButton("浏览")
        self.nineteenth_output_folder_button.clicked.connect(self.select_nineteenth_output_folder)

        # 第19步参数输入
        self.user_label = QLabel("USER 值 (默认 2):")
        self.user_entry = QLineEdit()
        self.user_entry.setText("2")

        self.tool_label = QLabel("TOOL 值 (默认 0):")
        self.tool_entry = QLineEdit()
        self.tool_entry.setText("0")

        # 类型选择下拉框
        self.type_labels = {}
        self.type_combos = {}
        for type_name, default_t in self.default_type_map.items():
            label = QLabel(type_name)
            combo = QComboBox()
            combo.addItems(["T0", "T1"])
            combo.setCurrentText(default_t)
            self.type_labels[type_name] = label
            self.type_combos[type_name] = combo

        # 偏移量输入框 (用于 ninth_step)
        self.offset_x_label = QLabel("X 偏移量 (默认 3.04):")
        self.offset_x_entry = QLineEdit()
        self.offset_x_entry.setText("3.04")

        self.offset_y_label = QLabel("Y 偏移量 (默认 -56.471):")
        self.offset_y_entry = QLineEdit()
        self.offset_y_entry.setText("-56.471")

        self.offset_z_label = QLabel("Z 偏移量 (默认 -3.11):")
        self.offset_z_entry = QLineEdit()
        self.offset_z_entry.setText("-3.11")

        # 第十一步参数输入框
        self.w_label = QLabel("线宽 W (默认 1.2):")
        self.w_entry = QLineEdit()
        self.w_entry.setText("1.2")

        self.h_label = QLabel("层厚 H (默认 0.2):")
        self.h_entry = QLineEdit()
        self.h_entry.setText("0.2")

        self.k2_label = QLabel("连续纤维挤出系数值 (默认 0.98):")
        self.k2_entry = QLineEdit()
        self.k2_entry.setText("0.98")

        self.f1_label = QLabel("F1 进给速度 (默认 1000):")
        self.f1_entry = QLineEdit()
        self.f1_entry.setText("1000")

        self.f2_label = QLabel("F2 进给速度 (默认 500):")
        self.f2_entry = QLineEdit()
        self.f2_entry.setText("500")

        # 第十二步参数输入框
        self.distance_label = QLabel("剪断距离 (mm):")
        self.distance_entry = QLineEdit()
        self.distance_entry.setPlaceholderText("例如: 5.0")

        self.insert_f_label = QLabel("初始移动速度:")
        self.insert_f_entry = QLineEdit()
        self.insert_f_entry.setPlaceholderText("例如: 300")

        self.connection_f_label = QLabel("跳转F值:")
        self.connection_f_entry = QLineEdit()
        self.connection_f_entry.setPlaceholderText("例如: 800")

        # 预挤出长度 J_distance 输入框
        self.j_distance_label = QLabel("预挤出长度 J_distance:")
        self.j_distance_entry = QLineEdit()
        self.j_distance_entry.setPlaceholderText("例如: 10.0")

        # 第二十步参数输入框：整体偏置坐标
        self.global_offset_x_label = QLabel("整体偏置坐标 X:")
        self.global_offset_x_entry = QLineEdit()
        self.global_offset_x_entry.setPlaceholderText("例如: 100.0")

        self.global_offset_y_label = QLabel("整体偏置坐标 Y:")
        self.global_offset_y_entry = QLineEdit()
        self.global_offset_y_entry.setPlaceholderText("例如: 200.0")

        self.global_offset_z_label = QLabel("整体偏置坐标 Z:")
        self.global_offset_z_entry = QLineEdit()
        self.global_offset_z_entry.setPlaceholderText("例如: 0.0")

        # 处理按钮
        self.process_button = QPushButton("开始处理")
        self.process_button.clicked.connect(self.process_files)

        # 设置布局
        layout = QVBoxLayout()

        # 输入文件布局
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(self.input_button)
        layout.addLayout(input_layout)

        # 第19步输出文件夹布局
        nineteenth_output_layout = QHBoxLayout()
        nineteenth_output_layout.addWidget(self.nineteenth_output_folder_label)
        nineteenth_output_layout.addWidget(self.nineteenth_output_folder_path)
        nineteenth_output_layout.addWidget(self.nineteenth_output_folder_button)
        layout.addLayout(nineteenth_output_layout)

        # 第19步参数布局
        nineteenth_params_layout = QVBoxLayout()
        nineteenth_params_layout.addWidget(self.user_label)
        nineteenth_params_layout.addWidget(self.user_entry)
        nineteenth_params_layout.addWidget(self.tool_label)
        nineteenth_params_layout.addWidget(self.tool_entry)
        layout.addLayout(nineteenth_params_layout)

        # 类型选择布局
        for type_name in self.default_type_map.keys():
            type_layout = QHBoxLayout()
            type_layout.addWidget(self.type_labels[type_name])
            type_layout.addWidget(self.type_combos[type_name])
            layout.addLayout(type_layout)

        # 偏移量输入布局 (用于 ninth_step)
        offset_layout = QVBoxLayout()
        offset_layout.addWidget(self.offset_x_label)
        offset_layout.addWidget(self.offset_x_entry)
        offset_layout.addWidget(self.offset_y_label)
        offset_layout.addWidget(self.offset_y_entry)
        offset_layout.addWidget(self.offset_z_label)
        offset_layout.addWidget(self.offset_z_entry)
        layout.addLayout(offset_layout)

        # 第十一步参数输入布局
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

        # 第十二步参数输入布局
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

        # 第二十步参数输入布局
        twentieth_step_params_layout = QVBoxLayout()
        twentieth_step_params_layout.addWidget(self.global_offset_x_label)
        twentieth_step_params_layout.addWidget(self.global_offset_x_entry)
        twentieth_step_params_layout.addWidget(self.global_offset_y_label)
        twentieth_step_params_layout.addWidget(self.global_offset_y_entry)
        twentieth_step_params_layout.addWidget(self.global_offset_z_label)
        twentieth_step_params_layout.addWidget(self.global_offset_z_entry)
        layout.addLayout(twentieth_step_params_layout)

        layout.addWidget(self.process_button)
        self.setLayout(layout)

    def select_input_file(self):
        """选择输入文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择输入文件", "", "G-code files (*.gcode)")
        if file_path:
            self.input_path.setText(file_path)

    def select_nineteenth_output_folder(self):
        """选择第19步输出文件夹"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择路径输出文件夹")
        if folder_path:
            self.nineteenth_output_folder_path.setText(folder_path)

    def process_files(self):
        """处理文件，依次调用所有步骤"""
        input_file = self.input_path.text()
        nineteenth_output_folder = self.nineteenth_output_folder_path.text()

        if not input_file:
            QMessageBox.warning(self, "错误", "请选择输入文件")
            return
        if not nineteenth_output_folder:
            QMessageBox.warning(self, "错误", "请选择路径输出文件夹")
            return

        # 获取 USER 和 TOOL 参数
        try:
            user = int(self.user_entry.text())
            tool = int(self.tool_entry.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的 用户坐标系 和 工具坐标系 值（整数）")
            return

        # 构建类型映射
        type_map = {type_name: combo.currentText() for type_name, combo in self.type_combos.items()}

        # 获取 ninth_step 偏移量
        try:
            offset_x = float(self.offset_x_entry.text())
            offset_y = float(self.offset_y_entry.text())
            offset_z = float(self.offset_z_entry.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的 ninth_step 偏移量（数字）")
            return

        # 获取第十一步参数
        try:
            w = float(self.w_entry.text())
            h = float(self.h_entry.text())
            k2 = float(self.k2_entry.text())
            f1 = float(self.f1_entry.text())
            f2 = float(self.f2_entry.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的第十一步参数（数字）")
            return

        # 获取第十二步参数
        try:
            distance = float(self.distance_entry.text())
            insert_f = float(self.insert_f_entry.text())
            connection_f = float(self.connection_f_entry.text())
            j_distance = float(self.j_distance_entry.text())
            j_offset = j_distance - distance  # 计算 j_offset
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的第十二步参数（数字）")
            return

        # 获取第二十步参数（整体偏置坐标）
        try:
            global_offset_x = float(self.global_offset_x_entry.text())
            global_offset_y = float(self.global_offset_y_entry.text())
            global_offset_z = float(self.global_offset_z_entry.text())
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入有效的整体偏置坐标（数字）")
            return

        try:
            # 定义中间文件路径
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
            intermediate_20 = "intermediate_20.gcode"  # 第二十步输出
            intermediate_18 = "intermediate_18.gcode"  # 第十八步输出

            # 执行处理步骤
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
            # 第二十步：调用 offset 脚本的函数
            twentieth_step(intermediate_17, intermediate_20, global_offset_x, global_offset_y, global_offset_z)
            eighteenth_step(intermediate_20, intermediate_18)
            nineteenth_step(intermediate_18, nineteenth_output_folder, user, tool)

            QMessageBox.information(self, "成功", f"所有处理步骤完成！第19步输出文件夹: {nineteenth_output_folder}")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GCodeProcessorApp()
    window.show()
    sys.exit(app.exec_())