import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QLineEdit, QGroupBox,
    QFormLayout, QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout, QOpenGLWidget,
    QStackedWidget, QButtonGroup, QWidget, QSpinBox, QSplitter, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
import numpy as np
import struct
from OpenGL.GL import *

# 从 readjson.py 导入函数
from readjson import sliceSTL, process_files
# 导入分类和映射函数
from jsonreclass import classify_json
from jsonpp import map_parameters
# 导入 materialui 和 equipmentui
import materialui
import equipmentui

# STLViewer 类（保持不变，省略代码）
class STLViewer(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = []  # 存储 STL 模型数据
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.scale = 1.0
        self.trans_x = 0.0
        self.trans_y = 0.0
        self.last_pos = None
        self.plane_size = 50.0

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.678, 0.847, 0.902, 1.0)
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_NORMALIZE)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height
        glFrustum(-aspect, aspect, -1.0, 1.0, 1.0, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.trans_x, self.trans_y, -5.0)
        glScalef(self.scale, self.scale, self.scale)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        glBegin(GL_TRIANGLES)
        glColor3f(0.8, 0.6, 0.2)
        for normal, vertices in self.model:
            glNormal3f(*normal)
            for vertex in vertices:
                glVertex3f(*vertex)
        glEnd()

        glDisable(GL_LIGHTING)
        glBegin(GL_LINES)
        glColor3f(0.5, 0.5, 0.5)
        step = self.plane_size / 10
        for i in np.arange(-self.plane_size, self.plane_size + step, step):
            glVertex3f(i, -self.plane_size, 0)
            glVertex3f(i, self.plane_size, 0)
            glVertex3f(-self.plane_size, i, 0)
            glVertex3f(self.plane_size, i, 0)
        glEnd()
        glEnable(GL_LIGHTING)

    def mousePressEvent(self, event):
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.last_pos is None:
            return
        dx = event.pos().x() - self.last_pos.x()
        dy = event.pos().y() - self.last_pos.y()
        if event.buttons() & Qt.LeftButton:
            self.rotation_x += dy * 0.5
            self.rotation_y += dx * 0.5
        elif event.buttons() & Qt.RightButton:
            self.trans_x += dx * 0.01
            self.trans_y -= dy * 0.01
        self.last_pos = event.pos()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 1200.0
        self.scale += delta
        if self.scale < 0.1:
            self.scale = 0.1
        self.update()

    def load_stl(self, file_path):
        self.model.clear()
        try:
            with open(file_path, 'rb') as f:
                f.read(80)
                num_triangles = struct.unpack('<I', f.read(4))[0]
                for _ in range(num_triangles):
                    data = f.read(50)
                    if len(data) < 50:
                        break
                    normal = struct.unpack('<3f', data[0:12])
                    vertices = [
                        struct.unpack('<3f', data[12:24]),
                        struct.unpack('<3f', data[24:36]),
                        struct.unpack('<3f', data[36:48]),
                    ]
                    self.model.append((normal, vertices))
                all_vertices = np.array([v for _, verts in self.model for v in verts])
                center = np.mean(all_vertices, axis=0)
                self.trans_x = -center[0]
                self.trans_y = -center[1]
                max_dim = np.max(np.max(all_vertices, axis=0) - np.min(all_vertices, axis=0))
                self.scale = 2.0 / max_dim if max_dim > 0 else 1.0
                self.plane_size = max_dim * 2
            self.update()
        except Exception as e:
            print(f"加载 STL 文件出错: {e}")

# GCodeViewer 类（保持不变，省略代码）
class GCodeViewer(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.paths = []
        self.rotation_x = 0.0
        self.rotation_y = 0.0
        self.scale = 1.0
        self.view_center_x = 0.0
        self.view_center_y = 0.0
        self.view_center_z = 0.0
        self.camera_distance = 0.0
        self.last_pos = None
        self.plane_size = 50.0
        self.total_points = 0
        self.progress = 0
        self.initialized = False

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glClearColor(0.7, 0.9, 1.0, 1.0)
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 10.0, 1.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_NORMALIZE)
        self.initialized = True

    def resizeGL(self, width, height):
        if not self.initialized:
            return
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = width / height
        glFrustum(-aspect, aspect, -1.0, 1.0, 1.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        if not self.initialized:
            return
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -self.camera_distance)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        glTranslatef(-self.view_center_x, -self.view_center_y, -self.view_center_z)
        glScalef(self.scale, self.scale, self.scale)

        glBegin(GL_LINES)
        points_drawn = 0
        for path in self.paths:
            for i in range(len(path) - 1):
                if points_drawn >= self.progress:
                    break
                start, end = path[i], path[i + 1]
                if 'E' in end and float(end['E']) > float(start.get('E', 0)):
                    glColor3f(1.0, 0.5, 0.0)
                elif 'J' in end and float(end['J']) > float(start.get('J', 0)):
                    glColor3f(0.0, 0.0, 1.0)
                else:
                    glColor3f(0.3, 0.3, 0.3)
                glVertex3f(start['X'], start['Y'], start['Z'])
                glVertex3f(end['X'], end['Y'], end['Z'])
                points_drawn += 1
            if points_drawn >= self.progress:
                break
        glEnd()

        glDisable(GL_LIGHTING)
        glBegin(GL_LINES)
        glColor3f(0.5, 0.5, 0.5)
        step = self.plane_size / 10
        for i in np.arange(-self.plane_size, self.plane_size + step, step):
            glVertex3f(i, -self.plane_size, 0)
            glVertex3f(i, self.plane_size, 0)
            glVertex3f(-self.plane_size, i, 0)
            glVertex3f(self.plane_size, i, 0)
        glEnd()
        glEnable(GL_LIGHTING)

    def mousePressEvent(self, event):
        if not self.initialized:
            return
        self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.initialized or self.last_pos is None:
            return
        dx = event.pos().x() - self.last_pos.x()
        dy = event.pos().y() - self.last_pos.y()
        if event.buttons() & Qt.LeftButton:
            self.view_center_x -= dx * 0.5 / self.scale
            self.view_center_y += dy * 0.5 / self.scale
        elif event.buttons() & Qt.RightButton:
            self.rotation_x += dy * 0.5
            self.rotation_y += dx * 0.5
        self.last_pos = event.pos()
        self.update()

    def wheelEvent(self, event):
        if not self.initialized:
            return
        delta = event.angleDelta().y() / 1200.0
        new_scale = self.scale + delta
        self.scale = max(0.01, min(100.0, new_scale))
        self.update()

    def load_gcode(self, file_path):
        if not self.initialized:
            return
        self.paths.clear()
        current_pos = {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'E': 0.0, 'J': 0.0}
        current_path = []
        self.total_points = 0
        x_min = y_min = z_min = float('inf')
        x_max = y_max = z_max = float('-inf')

        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(';'):
                    continue
                parts = line.split()
                if not parts or parts[0] not in ('G0', 'G1'):
                    continue
                new_pos = current_pos.copy()
                for param in parts[1:]:
                    if param.startswith('X'):
                        new_pos['X'] = float(param[1:])
                        x_min = min(x_min, new_pos['X'])
                        x_max = max(x_max, new_pos['X'])
                    elif param.startswith('Y'):
                        new_pos['Y'] = float(param[1:])
                        y_min = min(y_min, new_pos['Y'])
                        y_max = max(y_max, new_pos['Y'])
                    elif param.startswith('Z'):
                        new_pos['Z'] = float(param[1:])
                        z_min = min(z_min, new_pos['Z'])
                        z_max = max(z_max, new_pos['Z'])
                    elif param.startswith('E'):
                        new_pos['E'] = float(param[1:])
                    elif param.startswith('J'):
                        new_pos['J'] = float(param[1:])
                if current_path and current_pos['Z'] != new_pos['Z']:
                    self.paths.append(current_path)
                    current_path = [current_pos.copy()]
                current_path.append(new_pos.copy())
                current_pos = new_pos
                self.total_points += 1
        if current_path:
            self.paths.append(current_path)
            self.total_points += 1
        if self.paths:
            self.view_center_x = (x_min + x_max) / 2
            self.view_center_y = (y_min + y_max) / 2
            self.view_center_z = (z_min + z_max) / 2
            max_dim = max(x_max - x_min, y_max - y_min, z_max - z_min)
            self.camera_distance = max_dim * 1.5
            self.scale = 200.0 / max_dim if max_dim > 0 else 1.0
            self.plane_size = max_dim * 1.5
            self.progress = self.total_points
        self.update()

# 主窗口类
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-Code Viewer")
        self.resize(1200, 800)
        self.config_file_path = ""  # 初始化为空，需用户选择配置文件

        # 顶部布局
        top_layout = QVBoxLayout()
        config_layout = QHBoxLayout()
        self.load_config_button = QPushButton("加载配置文件")
        self.save_config_button = QPushButton("保存配置文件")
        self.config_path = QLineEdit()
        self.config_path.setReadOnly(True)
        self.run_slice_button = QPushButton("运行切片")
        config_layout.addWidget(self.load_config_button)
        config_layout.addWidget(self.save_config_button)
        config_layout.addWidget(self.config_path)
        config_layout.addStretch()
        config_layout.addWidget(self.run_slice_button)

        stl_layout = QHBoxLayout()
        self.load_stl_button = QPushButton("加载 STL")
        self.stl_path = QLineEdit()
        self.stl_path.setReadOnly(True)
        stl_layout.addWidget(self.load_stl_button)
        stl_layout.addWidget(self.stl_path)

        output_folder_layout = QHBoxLayout()
        self.select_output_folder_button = QPushButton("选择输出文件夹")
        self.output_folder_path = QLineEdit()
        self.output_folder_path.setReadOnly(True)
        output_folder_layout.addWidget(self.select_output_folder_button)
        output_folder_layout.addWidget(self.output_folder_path)

        top_layout.addLayout(config_layout)
        top_layout.addLayout(stl_layout)
        top_layout.addLayout(output_folder_layout)

        # 图形显示区域
        self.stl_viewer = STLViewer(self)
        self.gcode_viewer = GCodeViewer(self)
        self.stack_widget_gl = QStackedWidget()
        self.stack_widget_gl.addWidget(self.stl_viewer)
        self.stack_widget_gl.addWidget(self.gcode_viewer)

        # 参数设置面板
        params_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.layer_button = QPushButton("分层高度设置")
        self.material_button = QPushButton("耗材")
        self.device_button = QPushButton("设备")
        self.topology_button = QPushButton("拓扑结构路径")
        self.surface_button = QPushButton("曲面打印")
        button_layout.addWidget(self.layer_button)
        button_layout.addWidget(self.material_button)
        button_layout.addWidget(self.device_button)
        button_layout.addWidget(self.topology_button)
        button_layout.addWidget(self.surface_button)

        self.stack_widget = QStackedWidget()
        layer_panel = QGroupBox("分层高度设置")
        layer_layout = QVBoxLayout()
        layer_height_group = QGroupBox("层高")
        layer_height_layout = QFormLayout()
        self.layer_thickness = QLineEdit()
        self.layer_thickness.setValidator(QDoubleValidator(0.01, 10.0, 2))
        self.layer_thickness.setText("0.2")
        layer_height_layout.addRow("分层厚度 (mm)", self.layer_thickness)
        layer_height_group.setLayout(layer_height_layout)

        outline_group = QGroupBox("轮廓")
        outline_layout = QVBoxLayout()
        horizontal_shell_group = QGroupBox("水平外壳")
        horizontal_shell_layout = QFormLayout()
        self.bottom_layers = QSpinBox()
        self.bottom_layers.setRange(0, 100)
        self.bottom_layers.setValue(2)
        horizontal_shell_layout.addRow("底面层数", self.bottom_layers)
        self.top_layers = QSpinBox()
        self.top_layers.setRange(0, 100)
        self.top_layers.setValue(2)
        horizontal_shell_layout.addRow("顶面层数", self.top_layers)
        horizontal_shell_group.setLayout(horizontal_shell_layout)
        vertical_shell_group = QGroupBox("垂直外壳")
        vertical_shell_layout = QFormLayout()
        self.wall_loops = QSpinBox()
        self.wall_loops.setRange(1, 100)
        self.wall_loops.setValue(2)
        vertical_shell_layout.addRow("壁圈数", self.wall_loops)
        vertical_shell_group.setLayout(vertical_shell_layout)
        outline_layout.addWidget(horizontal_shell_group)
        outline_layout.addWidget(vertical_shell_group)
        outline_group.setLayout(outline_layout)

        support_group = QGroupBox("支撑")
        support_layout = QFormLayout()
        self.enable_support = QCheckBox("启用支撑")
        support_layout.addRow(self.enable_support)
        self.support_type = QComboBox()
        self.support_type.addItems(["网格", "树形", "线性"])
        self.support_type.setEnabled(False)
        support_layout.addRow("支撑构型", self.support_type)
        self.support_material = QComboBox()
        self.support_material.addItems(["PLA", "PVA", "PETG"])
        self.support_material.setEnabled(False)
        support_layout.addRow("打印材料", self.support_material)
        support_group.setLayout(support_layout)
        self.enable_support.stateChanged.connect(self.toggle_support_options)

        infill_group = QGroupBox("内部填充")
        infill_layout = QFormLayout()
        self.line_width = QLineEdit()
        self.line_width.setValidator(QDoubleValidator(0.1, 10.0, 2))
        self.line_width.setText("0.4")
        infill_layout.addRow("线宽 (mm)", self.line_width)
        self.infill_pattern = QComboBox()
        self.infill_pattern.addItems(["直线", "十字网格", "同心圆", "正六边形蜂窝"])
        infill_layout.addRow("填充构型", self.infill_pattern)
        infill_group.setLayout(infill_layout)

        extruder_group = QGroupBox("挤出机设置")
        extruder_layout = QFormLayout()
        self.infill_extruder = QComboBox()
        self.infill_extruder.addItems(["T0", "T1"])
        extruder_layout.addRow("填充:", self.infill_extruder)
        self.inner_wall_extruder = QComboBox()
        self.inner_wall_extruder.addItems(["T0", "T1"])
        extruder_layout.addRow("内壁:", self.inner_wall_extruder)
        self.outer_wall_extruder = QComboBox()
        self.outer_wall_extruder.addItems(["T0", "T1"])
        extruder_layout.addRow("外壁:", self.outer_wall_extruder)
        self.support_extruder = QComboBox()
        self.support_extruder.addItems(["T0", "T1"])
        extruder_layout.addRow("支撑:", self.support_extruder)
        self.surface_support_extruder = QComboBox()
        self.surface_support_extruder.addItems(["T0", "T1"])
        extruder_layout.addRow("表面支撑:", self.surface_support_extruder)
        self.skin_extruder = QComboBox()
        self.skin_extruder.addItems(["T0", "T1"])
        extruder_layout.addRow("皮肤（底/顶）:", self.skin_extruder)
        self.skirt_extruder = QComboBox()
        self.skirt_extruder.addItems(["T0", "T1"])
        extruder_layout.addRow("裙边:", self.skirt_extruder)
        extruder_group.setLayout(extruder_layout)

        layer_layout.addWidget(layer_height_group)
        layer_layout.addWidget(outline_group)
        layer_layout.addWidget(support_group)
        layer_layout.addWidget(infill_group)
        layer_layout.addWidget(extruder_group)
        layer_panel.setLayout(layer_layout)
        self.stack_widget.addWidget(layer_panel)

        # 添加 materialui 和 equipmentui 面板
        self.material_settings = materialui.MaterialSettingsWidget(self)
        self.stack_widget.addWidget(self.material_settings)  # 耗材设置
        self.device_settings = equipmentui.DeviceSettingsWidget(self)
        self.stack_widget.addWidget(self.device_settings)  # 设备设置
        self.stack_widget.addWidget(QWidget())  # 拓扑结构路径占位
        self.stack_widget.addWidget(QWidget())  # 曲面打印占位

        params_layout.addLayout(button_layout)
        params_layout.addWidget(self.stack_widget)

        # 整体布局
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addLayout(top_layout)
        left_layout.addWidget(self.stack_widget_gl)
        left_widget.setLayout(left_layout)

        params_widget = QWidget()
        params_widget.setLayout(params_layout)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(params_widget)

        central_widget = QWidget()
        central_widget.setLayout(QVBoxLayout())
        central_widget.layout().addWidget(splitter)
        self.setCentralWidget(central_widget)

        # 按钮组
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.layer_button, 0)
        self.button_group.addButton(self.material_button, 1)
        self.button_group.addButton(self.device_button, 2)
        self.button_group.addButton(self.topology_button, 3)
        self.button_group.addButton(self.surface_button, 4)
        self.button_group.buttonClicked.connect(self.switch_panel)

        # 事件绑定
        self.load_config_button.clicked.connect(self.load_config)
        self.save_config_button.clicked.connect(self.save_config)
        self.run_slice_button.clicked.connect(self.run_slice)
        self.load_stl_button.clicked.connect(self.load_stl)
        self.select_output_folder_button.clicked.connect(self.select_output_folder)

        # 参数映射
        self.support_type_map = {"网格": "grid", "树形": "tree", "线性": "lines"}
        self.infill_pattern_map = {"直线": "lines", "十字网格": "cross", "同心圆": "concentric", "正六边形蜂窝": "hexagonal"}
        self.support_type_map_rev = {v: k for k, v in self.support_type_map.items()}
        self.infill_pattern_map_rev = {v: k for k, v in self.infill_pattern_map.items()}

    def switch_panel(self, button):
        index = self.button_group.id(button)
        self.stack_widget.setCurrentIndex(index)

    def load_config(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "打开配置文件", "", "Config Files (*.json)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                temp_classified_file = "temp_classified_config.json"
                classify_json(file_name, temp_classified_file)

                with open(temp_classified_file, 'r', encoding='utf-8') as f:
                    classified_data = json.load(f)

                mapped_data = map_parameters(classified_data)

                output_file = os.path.splitext(file_name)[0] + "_processed.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(mapped_data, f, indent=4, ensure_ascii=False)

                self.update_ui_from_config(data)
                self.config_file_path = file_name
                self.config_path.setText(file_name)
                QMessageBox.information(self, "成功", f"配置文件已处理并保存为 {output_file}")

                os.remove(temp_classified_file)

            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载或处理配置文件失败: {str(e)}")

    def update_ui_from_config(self, config):
        self.layer_thickness.setText(str(config.get('layer_thickness', '0.2')))
        self.bottom_layers.setValue(int(config.get('bottom_layers', 2)))
        self.top_layers.setValue(int(config.get('top_layers', 2)))
        self.wall_loops.setValue(int(config.get('wall_loops', 2)))
        self.enable_support.setChecked(config.get('enable_support', False))
        support_type_en = config.get('support_type', 'grid')
        self.support_type.setCurrentText(self.support_type_map_rev.get(support_type_en, "网格"))
        self.support_material.setCurrentText(config.get('support_material', 'PLA'))
        self.line_width.setText(str(config.get('line_width', '0.4')))
        infill_pattern_en = config.get('infill_pattern', 'lines')
        self.infill_pattern.setCurrentText(self.infill_pattern_map_rev.get(infill_pattern_en, "直线"))
        self.infill_extruder.setCurrentText(config.get('infill_extruder', 'T0'))
        self.inner_wall_extruder.setCurrentText(config.get('inner_wall_extruder', 'T0'))
        self.outer_wall_extruder.setCurrentText(config.get('outer_wall_extruder', 'T0'))
        self.support_extruder.setCurrentText(config.get('support_extruder', 'T0'))
        self.surface_support_extruder.setCurrentText(config.get('surface_support_extruder', 'T0'))
        self.skin_extruder.setCurrentText(config.get('skin_extruder', 'T0'))
        self.skirt_extruder.setCurrentText(config.get('skirt_extruder', 'T0'))
        # 更新 materialui 和 equipmentui 的配置
        self.material_settings.set_config(config.get('material_settings', {}))
        self.device_settings.set_config(config.get('device_settings', {}))

    def save_config(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "保存配置文件", "", "Config Files (*.json)")
        if file_name:
            support_type_en = self.support_type_map.get(self.support_type.currentText(), "grid")
            infill_pattern_en = self.infill_pattern_map.get(self.infill_pattern.currentText(), "lines")
            config = {
                'layer_thickness': self.layer_thickness.text(),
                'bottom_layers': self.bottom_layers.value(),
                'top_layers': self.top_layers.value(),
                'wall_loops': self.wall_loops.value(),
                'enable_support': self.enable_support.isChecked(),
                'support_type': support_type_en,
                'support_material': self.support_material.currentText(),
                'line_width': self.line_width.text(),
                'infill_pattern': infill_pattern_en,
                'infill_extruder': self.infill_extruder.currentText(),
                'inner_wall_extruder': self.inner_wall_extruder.currentText(),
                'outer_wall_extruder': self.outer_wall_extruder.currentText(),
                'support_extruder': self.support_extruder.currentText(),
                'surface_support_extruder': self.surface_support_extruder.currentText(),
                'skin_extruder': self.skin_extruder.currentText(),
                'skirt_extruder': self.skirt_extruder.currentText(),
                'material_settings': self.material_settings.get_config(),
                'device_settings': self.device_settings.get_config(),
                'json_config': {
                    'layer_height': float(self.layer_thickness.text()),
                    'line_width': float(self.line_width.text())
                },
                'gcode_processor': {
                    'type_map': {},
                    'offset_x': 3.04,
                    'offset_y': -56.471,
                    'offset_z': -3.11,
                    'w': 1.2,
                    'h': 0.2,
                    'k2': 0.98,
                    'f1': 1000.0,
                    'f2': 500.0,
                    'distance': 5.0,
                    'insert_f': 300.0,
                    'connection_f': 800.0,
                    'j_distance': 10.0,
                    'global_offset_x': 120.0,
                    'global_offset_y': 200.0,
                    'global_offset_z': 0.0,
                    'user': 2,
                    'tool': 0
                }
            }
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=4, ensure_ascii=False)
                self.config_path.setText(file_name)
                self.config_file_path = file_name
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存配置文件失败: {str(e)}")

    def run_slice(self):
        stl_path = self.stl_path.text()
        output_folder = self.output_folder_path.text()
        if not stl_path or not output_folder:
            QMessageBox.warning(self, "警告", "请先选择 STL 文件和输出文件夹")
            return

        processed_config_file = os.path.splitext(self.config_file_path)[0] + "_processed.json"
        if not os.path.exists(processed_config_file):
            QMessageBox.warning(self, "警告", f"中间配置文件 {processed_config_file} 不存在，请先加载并处理配置文件")
            return

        try:
            stl_path = os.path.abspath(stl_path)
            output_folder = os.path.abspath(output_folder)

            with open(processed_config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            config_data['json_config']['layer_height'] = float(self.layer_thickness.text())
            config_data['json_config']['line_width'] = float(self.line_width.text())

            gcode_file = sliceSTL(stl_path, output_folder, config_data)
            if gcode_file:
                process_files(gcode_file, output_folder, config_data)
                gcode_path = os.path.join(output_folder, "intermediate_20.gcode")
                if os.path.exists(gcode_path):
                    self.gcode_viewer.load_gcode(gcode_path)
                    self.stack_widget_gl.setCurrentWidget(self.gcode_viewer)
                else:
                    QMessageBox.critical(self, "错误", f"文件 {gcode_path} 不存在")
            else:
                QMessageBox.critical(self, "错误", "切片失败，未生成 G-code 文件")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"操作失败: {str(e)}")

    def load_stl(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "打开 STL 文件", "", "STL Files (*.stl)")
        if file_name:
            self.stl_viewer.load_stl(file_name)
            self.stl_path.setText(file_name)
            self.stack_widget_gl.setCurrentWidget(self.stl_viewer)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.output_folder_path.setText(folder)

    def toggle_support_options(self, state):
        self.support_type.setEnabled(state == Qt.Checked)
        self.support_material.setEnabled(state == Qt.Checked)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())