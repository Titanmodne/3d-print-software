import sys
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
                             QMessageBox, QHBoxLayout, QComboBox, QDoubleSpinBox, QSpinBox)

class JsonConfigEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.json_data = None
        self.file_path = ""

    def initUI(self):
        self.layout = QVBoxLayout()

        # 参数和中文标签对应表，包含参数的访问路径
        self.parameters = {
                "layer_height": ("层高", "float", ["settings", "resolution", "children", "layer_height", "default_value"], 0.001, 0.8),
                "layer_height_0": ("起始层高", "float", ["settings", "resolution", "children", "layer_height_0", "default_value"], 0.001, 0.8),
                "line_width": ("走线宽度", "float", ["settings", "resolution", "children", "line_width", "default_value"], 0.001, 2),
                "wall_line_width": ("走线宽度(壁)", "float",["settings", "resolution", "children", "line_width", "children", "wall_line_width","default_value"], 0.001, 2),
                "wall_line_width_0": ("走线宽度(外壁)", "float",["settings", "resolution", "children", "line_width", "children", "wall_line_width","children", "wall_line_width_0", "default_value"], 0.001, 2),
                "wall_line_width_x": ("走线宽度(内壁)", "float",["settings", "resolution", "children", "line_width", "children", "wall_line_width","children", "wall_line_width_x", "default_value"], 0.001, 2),
                "infill_line_width": ("走线宽度(填充)", "float",["settings", "resolution", "children", "line_width", "children", "infill_line_width","default_value"], 0.001, 3),
                "initial_layer_line_width_factor": ("起始层线宽", "float", ["settings", "resolution", "children","initial_layer_line_width_factor","default_value"], 0.001, 150),
                "wall_thickness": ("壁厚", "float", ["settings", "shell", "children", "wall_thickness", "default_value"], 0, 999999),"wall_line_count": ("壁走线次数", "int",["settings", "shell", "children", "wall_thickness", "children", "wall_line_count","default_value"], 0, 999999),
                "optimize_wall_printing_order": ("优化壁打印顺序", "bool",["settings", "shell", "children", "optimize_wall_printing_order","default_value"]),
                "wall_ordering": ("壁顺序", "enum", ["settings", "shell", "children", "inset_direction", "default_value"],["inside_out", "outside_in"]),
                "z_seam_type": ("Z缝对齐", "enum", ["settings", "shell", "children", "z_seam_type", "default_value"],["back", "shortest", "random", "sharpest_corner"]),
                "top_bottom_thickness": ("顶层/底层厚度", "float", ["settings", "top_bottom", "children", "top_bottom_thickness", "default_value"],0.2, 10),
                "top_thickness": ("顶层厚度", "float",["settings", "top_bottom", "children", "top_bottom_thickness", "children","top_thickness", "default_value"], 0.2, 10),
                "top_layers": ("顶部层数", "int",["settings", "top_bottom", "children", "top_bottom_thickness", "children", "top_thickness","children", "top_layers", "default_value"], 0, 100),
                "bottom_thickness": ("底层厚度", "float",["settings", "top_bottom", "children", "top_bottom_thickness", "children","bottom_thickness", "default_value"], 0.2, 10),
                "bottom_layers": ("底部层数", "int",["settings", "top_bottom", "children", "top_bottom_thickness", "children","bottom_thickness", "children", "bottom_layers", "default_value"], 0, 100),
                "initial_bottom_layers": ("初始底层数", "int",["settings", "top_bottom", "children", "top_bottom_thickness", "children","bottom_thickness", "children", "initial_bottom_layers", "default_value"], 0,100),
                "infill_sparse_density": ("填充密度", "float", ["settings", "infill", "children", "infill_sparse_density", "default_value"], 0, 100),
                "infill_line_distance": ("填充走线距离", "float",["settings", "infill", "children", "infill_sparse_density", "children","infill_line_distance", "default_value"], 0, 10),
                "infill_pattern": ("填充图案", "enum", ["settings", "infill", "children", "infill_pattern", "default_value"],["grid", "lines", "triangles", "trihexagon", "cubic", "cubicsubdiv"]),
                "connect_infill_lines": ("连接填充走线", "bool", ["settings", "infill", "children", "connect_infill_polygons", "default_value"]),
                "infill_multiplier": ("填充走线乘数", "float", ["settings", "infill", "children", "infill_multiplier", "default_value"], 0.1, 10),
                "infill_overlap_percentage": ("填充重叠百分比", "float", ["settings", "infill", "children", "infill_overlap", "default_value"], 0, 100),
                "infill_overlap_mm": ("填充重叠(mm)", "float",["settings", "infill", "children", "infill_overlap", "children", "infill_overlap_mm","default_value"], 0, 10),
                "infill_wipe_distance": ("填充物擦拭距离", "float", ["settings", "infill", "children", "infill_wipe_dist", "default_value"], 0, 10),
                "infill_sparse_thickness": ("填充层厚度", "float", ["settings", "infill", "children", "infill_sparse_thickness", "default_value"], 0.1,10)
            # 每个参数包括访问路径，使得访问更具有通用性和灵活性
        }

        # 添加标签和输入控件
        self.inputs = {}
        for key, (label, type_, path, *range_) in self.parameters.items():
            row = QHBoxLayout()
            label_widget = QLabel(label)
            row.addWidget(label_widget)

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
            row.addWidget(input_widget)
            self.layout.addLayout(row)

        # 保存按钮
        self.btnSave = QPushButton('保存更改', self)
        self.btnSave.clicked.connect(self.saveChanges)
        self.layout.addWidget(self.btnSave)

        # 加载按钮
        self.btnLoad = QPushButton('加载 JSON', self)
        self.btnLoad.clicked.connect(self.loadJson)
        self.layout.addWidget(self.btnLoad)

        self.setLayout(self.layout)
        self.setGeometry(300, 300, 350, 600)
        self.setWindowTitle('JSON 配置编辑器')

    def loadJson(self):
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "选择 JSON 配置文件", "",
                                                        "All Files (*);;JSON Files (*.json)", options=options)
        if self.file_path:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    self.json_data = json.load(file)
                self.populateFields()
            except json.JSONDecodeError as e:
                QMessageBox.critical(self, "错误", f"JSON 文件格式不正确:\n{str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载 JSON 文件时发生错误:\n{str(e)}")

    def populateFields(self):
        for key, (widget, path) in self.inputs.items():
            try:
                value = self.get_value_from_path(path)
                if value is not None:
                    if isinstance(widget, (QDoubleSpinBox, QSpinBox)):
                        widget.setValue(value)
                    elif isinstance(widget, QComboBox) and isinstance(value, bool):
                        widget.setCurrentIndex(widget.findText(str(value).lower()))
                    elif isinstance(widget, QComboBox):  # for enum
                        widget.setCurrentText(value)
            except Exception as e:
                print(f"无法加载字段 {key}: {e}")

    def saveChanges(self):
        if not self.json_data or not self.file_path:
            QMessageBox.warning(self, "错误", "未加载 JSON 文件。")
            return

        for key, (widget, path) in self.inputs.items():
            value = widget.value() if isinstance(widget, (QDoubleSpinBox, QSpinBox)) else widget.currentText()
            if isinstance(widget, QComboBox) and self.parameters[key][1] == "bool":
                value = widget.currentText() == "true"
            self.set_value_from_path(path, value)

        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.json_data, file, indent=4, ensure_ascii=False)
        QMessageBox.information(self, "成功", "更改已成功保存。")

    def get_value_from_path(self, path):
        data = self.json_data
        for p in path:
            data = data.get(p, None)
            if data is None:
                return None
        return data

    def set_value_from_path(self, path, value):
        data = self.json_data
        for p in path[:-1]:
            data = data.setdefault(p, {})
        data[path[-1]] = value

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JsonConfigEditor()
    ex.show()
    sys.exit(app.exec_())
