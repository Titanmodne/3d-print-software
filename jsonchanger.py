import sys
import json
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
                             QMessageBox, QHBoxLayout, QComboBox, QDoubleSpinBox, QSpinBox, QTabWidget, QLineEdit)
from PyQt5.QtCore import Qt

class JsonConfigEditor(QWidget):
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        # 定义参数字典
        self.parameters = {
            "layer_height": ("层高", "float", ["settings", "resolution", "children", "layer_height", "default_value"], 0.001, 0.8),
            "layer_height_0": ("起始层高", "float", ["settings", "resolution", "children", "layer_height_0", "default_value"], 0.001, 0.8),
            "line_width": ("走线宽度", "float", ["settings", "resolution", "children", "line_width", "default_value"], 0.001, 10),
            "wall_line_width": ("走线宽度(壁)", "float", ["settings", "resolution", "children", "line_width", "children", "wall_line_width", "default_value"], 0.001, 10),
            "wall_line_width_0": ("走线宽度(外壁)", "float", ["settings", "resolution", "children", "line_width", "children","wall_line_width","children", "wall_line_width_0", "default_value"], 0.001, 10),
            "wall_line_width_x": ("走线宽度(内壁)", "float", ["settings", "resolution", "children", "line_width", "children","wall_line_width","children", "wall_line_width_x", "default_value"], 0.001, 10),
            "initial_layer_line_width_factor": ("起始层线宽", "float", ["settings", "resolution", "children", "initial_layer_line_width_factor", "default_value"], 0.001, 150),
            "wall_thickness": ("壁厚", "float", ["settings", "shell", "children", "wall_thickness", "default_value"], 0, 999999),
            "wall_line_count": ("壁走线次数", "int", ["settings", "shell", "children", "wall_thickness", "children", "wall_line_count", "default_value"], 0, 999999),
            "wall_ordering": ("壁顺序", "enum", ["settings", "shell", "children", "inset_direction", "default_value"], ["inside_out", "outside_in"]),
            "top_bottom_thickness": ("顶层/底层厚度", "float", ["settings", "top_bottom", "children", "top_bottom_thickness", "default_value"], 0.2, 10),
            "top_thickness": ("顶层厚度", "float", ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "top_thickness", "default_value"], 0.2, 10),
            "top_layers": ("顶部层数", "int", ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "top_thickness", "children", "top_layers", "default_value"], 0, 100),
            "bottom_thickness": ("底层厚度", "float", ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "bottom_thickness", "default_value"], 0.2, 10),
            "bottom_layers": ("底部层数", "int", ["settings", "top_bottom", "children", "top_bottom_thickness", "children", "bottom_thickness", "children", "bottom_layers", "default_value"], 0, 100),
            "infill_sparse_density": ("填充密度", "float", ["settings", "infill", "children", "infill_sparse_density", "default_value"], 0, 100),
            "infill_line_distance": ("填充走线距离", "float", ["settings", "infill", "children", "infill_sparse_density", "children", "infill_line_distance", "default_value"], 0, 10),
            "infill_pattern": ("填充图案", "enum", ["settings", "infill", "children", "infill_pattern", "default_value"], ["grid", "lines", "triangles", "trihexagon", "cubic", "cubicsubdiv"]),
            "infill_sparse_thickness": ("填充层厚度", "float", ["settings", "infill", "children", "infill_sparse_thickness", "default_value"], 0.1, 10),
            "skin_line_width": ("皮肤走线宽度", "float", ["settings", "resolution", "children", "skin_line_width", "default_value"], 0.001, 10)
        }
        self.inputs = {}
        self.json_data = None
        self.file_path = r"C:\Program Files\UltiMaker Cura 5.8.1\share\cura\resources\definitions\fdmprinter.def.json"
        self.initUI()
        self.loadJson()
        if config:
            self.load_config(config)

    def initUI(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        layout.addWidget(self.tabWidget)

        # 参数分组
        groups = {
            "层高设置": ["layer_height", "layer_height_0"],
            "走线宽度设置": ["line_width", "wall_line_width", "wall_line_width_0", "wall_line_width_x", "initial_layer_line_width_factor", "skin_line_width"],
            "壁设置": ["wall_thickness", "wall_line_count", "wall_ordering"],
            "顶层/底层设置": ["top_bottom_thickness", "top_thickness", "top_layers", "bottom_thickness", "bottom_layers"],
            "填充设置": ["infill_sparse_density", "infill_line_distance", "infill_pattern", "infill_sparse_thickness"]
        }

        # 创建选项卡
        for tab_name, keys in groups.items():
            tab = QWidget()
            tab_layout = QVBoxLayout()
            for key in keys:
                self.addParameterToLayout(key, tab_layout)
            tab.setLayout(tab_layout)
            self.tabWidget.addTab(tab, tab_name)

        # 添加按钮
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
        """将参数添加到布局中"""
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
        """加载 JSON 文件"""
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
        """填充字段值"""
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
        """根据路径获取值"""
        data = self.json_data
        for p in path:
            data = data.get(p, None)
            if data is None:
                return None
        return data

    def saveChanges(self):
        """保存更改到 JSON 文件"""
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
        """根据路径设置值"""
        data = self.json_data
        for p in path[:-1]:
            data = data.setdefault(p, {})
        data[path[-1]] = value

    def saveFullConfig(self):
        """保存完整配置文件"""
        self.window().save_config()

    def loadFullConfig(self):
        """加载完整配置文件"""
        self.window().load_new_config()

    def sliceSTL(self):
        """切片 STL 文件"""
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
            except subprocess.CalledProcessError as e:
                QMessageBox.critical(self, "切片失败", f"切片过程中发生错误: {str(e)}")

    def load_config(self, config):
        """加载配置"""
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
        """获取当前配置"""
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

class JsonEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON 配置编辑器")
        self.setGeometry(100, 100, 800, 600)
        self.config_file = "json_editor_config.json"
        self.config_data = self.load_config()

        self.json_editor = JsonConfigEditor(self, self.config_data.get("json_config", {}))
        self.setCentralWidget(self.json_editor)

    def load_config(self):
        """加载主窗口配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"加载配置文件失败: {str(e)}")
        return {"json_config": {}}

    def save_config(self):
        """保存主窗口配置"""
        config = {"json_config": self.json_editor.get_config()}
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "成功", f"配置文件已保存至: {self.config_file}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置文件失败: {str(e)}")

    def load_new_config(self):
        """加载新的配置文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "加载配置文件", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.json_editor.load_config(config.get("json_config", {}))
                QMessageBox.information(self, "成功", f"已加载配置文件: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载配置文件失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor_app = JsonEditorApp()
    editor_app.show()
    sys.exit(app.exec_())