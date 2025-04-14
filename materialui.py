import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGroupBox, QComboBox, QLineEdit, QPushButton,
    QDialog, QFormLayout, QLabel, QVBoxLayout, QHBoxLayout, QDoubleSpinBox,
    QSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt


# 对话框：添加新连续纤维材料
class ContinuousMaterialDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新连续纤维材料")
        layout = QFormLayout()

        self.name_input = QLineEdit()
        layout.addRow("材料名称:", self.name_input)

        self.temp_min = QDoubleSpinBox()
        self.temp_min.setRange(0, 1000)
        self.temp_min.setSuffix(" °C")
        layout.addRow("最低推荐打印温度:", self.temp_min)

        self.temp_max = QDoubleSpinBox()
        self.temp_max.setRange(0, 1000)
        self.temp_max.setSuffix(" °C")
        layout.addRow("最高推荐打印温度:", self.temp_max)

        self.spacing_min = QDoubleSpinBox()
        self.spacing_min.setRange(0, 100)
        self.spacing_min.setSuffix(" mm")
        layout.addRow("最低推荐打印间距:", self.spacing_min)

        self.spacing_max = QDoubleSpinBox()
        self.spacing_max.setRange(0, 100)
        self.spacing_max.setSuffix(" mm")
        layout.addRow("最高推荐打印间距:", self.spacing_max)

        self.layer_min = QDoubleSpinBox()
        self.layer_min.setRange(0, 10)
        self.layer_min.setSuffix(" mm")
        layout.addRow("最低推荐层高:", self.layer_min)

        self.layer_max = QDoubleSpinBox()
        self.layer_max.setRange(0, 10)
        self.layer_max.setSuffix(" mm")
        layout.addRow("最高推荐层高:", self.layer_max)

        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)


# 对话框：添加新辅助材料
class AuxiliaryMaterialDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新辅助材料")
        layout = QFormLayout()

        self.name_input = QLineEdit()
        layout.addRow("材料名称:", self.name_input)

        self.temp_min = QDoubleSpinBox()
        self.temp_min.setRange(0, 1000)
        self.temp_min.setSuffix(" °C")
        layout.addRow("最低推荐打印温度:", self.temp_min)

        self.temp_max = QDoubleSpinBox()
        self.temp_max.setRange(0, 1000)
        self.temp_max.setSuffix(" °C")
        layout.addRow("最高推荐打印温度:", self.temp_max)

        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)


# 耗材设置 Widget
class MaterialSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 数据文件
        self.data_file = "materials.json"
        self.continuous_materials = {}
        self.auxiliary_materials = {}
        self.load_materials()

        # 主布局
        main_layout = QVBoxLayout()

        # 连续纤维打印头材料
        continuous_group = QGroupBox("连续纤维打印头材料")
        continuous_layout = QFormLayout()

        # 材料选择
        self.continuous_material_combo = QComboBox()
        self.update_continuous_material_combo()
        continuous_layout.addRow("材料:", self.continuous_material_combo)

        # 添加新材料按钮
        self.add_continuous_btn = QPushButton("添加新材料")
        self.add_continuous_btn.clicked.connect(self.add_continuous_material)
        continuous_layout.addRow(self.add_continuous_btn)

        # 材料参数展示
        self.material_params_label = QLabel()
        continuous_layout.addRow("材料参数:", self.material_params_label)
        self.continuous_material_combo.currentIndexChanged.connect(self.update_material_params)

        # 挤出率
        self.extrusion_rate = QDoubleSpinBox()
        self.extrusion_rate.setRange(0.98, 1.00)
        self.extrusion_rate.setDecimals(3)
        self.extrusion_rate.setValue(0.998)
        continuous_layout.addRow("挤出率:", self.extrusion_rate)

        # 速度
        self.normal_speed = QSpinBox()
        self.normal_speed.setRange(0, 10000)
        self.normal_speed.setSuffix(" mm/s")
        self.normal_speed.setValue(500)
        continuous_layout.addRow("正常打印速度:", self.normal_speed)

        self.initial_speed = QSpinBox()
        self.initial_speed.setRange(0, 10000)
        self.initial_speed.setSuffix(" mm/s")
        self.initial_speed.setValue(300)
        continuous_layout.addRow("初始打印速度:", self.initial_speed)

        self.lift_speed = QSpinBox()
        self.lift_speed.setRange(0, 10000)
        self.lift_speed.setSuffix(" mm/s")
        self.lift_speed.setValue(800)
        continuous_layout.addRow("抬起和移动速度:", self.lift_speed)

        continuous_group.setLayout(continuous_layout)
        main_layout.addWidget(continuous_group)

        # 辅助打印头材料
        auxiliary_group = QGroupBox("辅助打印头材料")
        auxiliary_layout = QFormLayout()

        # 材料选择
        self.auxiliary_material_combo = QComboBox()
        self.update_auxiliary_material_combo()
        auxiliary_layout.addRow("材料:", self.auxiliary_material_combo)

        # 添加新材料按钮
        self.add_auxiliary_btn = QPushButton("添加新材料")
        self.add_auxiliary_btn.clicked.connect(self.add_auxiliary_material)
        auxiliary_layout.addRow(self.add_auxiliary_btn)

        # 辅助材料参数展示
        self.auxiliary_params_label = QLabel()
        auxiliary_layout.addRow("辅助材料参数:", self.auxiliary_params_label)
        self.auxiliary_material_combo.currentIndexChanged.connect(self.update_auxiliary_params)

        # 速度
        self.print_speed = QSpinBox()
        self.print_speed.setRange(0, 10000)
        self.print_speed.setSuffix(" mm/s")
        self.print_speed.setValue(500)
        auxiliary_layout.addRow("打印速度:", self.print_speed)

        auxiliary_group.setLayout(auxiliary_layout)
        main_layout.addWidget(auxiliary_group)

        # 设置主布局
        self.setLayout(main_layout)

    def update_continuous_material_combo(self):
        self.continuous_material_combo.clear()
        self.continuous_material_combo.addItems(
            ["1KCCFPA", "2KCCFPA", "CCFPLA"] + list(self.continuous_materials.keys()))

    def update_auxiliary_material_combo(self):
        self.auxiliary_material_combo.clear()
        self.auxiliary_material_combo.addItems(["PLA", "ABS"] + list(self.auxiliary_materials.keys()))

    def update_material_params(self):
        material = self.continuous_material_combo.currentText()
        if material in self.continuous_materials:
            params = self.continuous_materials[material]
            text = (f"温度: {params['temp_min']}°C - {params['temp_max']}°C\n"
                    f"间距: {params['spacing_min']}mm - {params['spacing_max']}mm\n"
                    f"层高: {params['layer_min']}mm - {params['layer_max']}mm")
            self.material_params_label.setText(text)
        elif material in ["1KCCFPA", "2KCCFPA", "CCFPLA"]:
            text = "预设材料参数\n温度: 200°C - 220°C\n间距: 0.4mm - 0.6mm\n层高: 0.1mm - 0.3mm"
            self.material_params_label.setText(text)
        else:
            self.material_params_label.setText("")

    def update_auxiliary_params(self):
        material = self.auxiliary_material_combo.currentText()
        if material in self.auxiliary_materials:
            params = self.auxiliary_materials[material]
            text = f"温度: {params['temp_min']}°C - {params['temp_max']}°C"
            self.auxiliary_params_label.setText(text)
        elif material in ["PLA", "ABS"]:
            text = "预设材料参数\n温度: 190°C - 230°C"
            self.auxiliary_params_label.setText(text)
        else:
            self.auxiliary_params_label.setText("")

    def add_continuous_material(self):
        dialog = ContinuousMaterialDialog(self)
        if dialog.exec_():
            name = dialog.name_input.text()
            if name and name not in self.continuous_materials:
                self.continuous_materials[name] = {
                    "temp_min": dialog.temp_min.value(),
                    "temp_max": dialog.temp_max.value(),
                    "spacing_min": dialog.spacing_min.value(),
                    "spacing_max": dialog.spacing_max.value(),
                    "layer_min": dialog.layer_min.value(),
                    "layer_max": dialog.layer_max.value()
                }
                self.update_continuous_material_combo()
                self.continuous_material_combo.setCurrentText(name)
                self.save_materials()
            else:
                QMessageBox.warning(self, "错误", "材料名称不能为空或已存在")

    def add_auxiliary_material(self):
        dialog = AuxiliaryMaterialDialog(self)
        if dialog.exec_():
            name = dialog.name_input.text()
            if name and name not in self.auxiliary_materials:
                self.auxiliary_materials[name] = {
                    "temp_min": dialog.temp_min.value(),
                    "temp_max": dialog.temp_max.value()
                }
                self.update_auxiliary_material_combo()
                self.auxiliary_material_combo.setCurrentText(name)
                self.save_materials()
            else:
                QMessageBox.warning(self, "错误", "材料名称不能为空或已存在")

    def load_materials(self):
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)
                self.continuous_materials = data.get("continuous", {})
                self.auxiliary_materials = data.get("auxiliary", {})
        except FileNotFoundError:
            pass

    def save_materials(self):
        data = {
            "continuous": self.continuous_materials,
            "auxiliary": self.auxiliary_materials
        }
        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=4)

    def get_config(self):
        """返回耗材配置字典"""
        return {
            'continuous_material': self.continuous_material_combo.currentText(),
            'extrusion_rate': self.extrusion_rate.value(),
            'normal_speed': self.normal_speed.value(),
            'initial_speed': self.initial_speed.value(),
            'lift_speed': self.lift_speed.value(),
            'auxiliary_material': self.auxiliary_material_combo.currentText(),
            'print_speed': self.print_speed.value(),
        }

    def set_config(self, config):
        """从字典加载耗材配置"""
        self.continuous_material_combo.setCurrentText(config.get('continuous_material', '1KCCFPA'))
        self.extrusion_rate.setValue(config.get('extrusion_rate', 0.998))
        self.normal_speed.setValue(config.get('normal_speed', 500))
        self.initial_speed.setValue(config.get('initial_speed', 300))
        self.lift_speed.setValue(config.get('lift_speed', 800))
        self.auxiliary_material_combo.setCurrentText(config.get('auxiliary_material', 'PLA'))
        self.print_speed.setValue(config.get('print_speed', 500))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MaterialSettingsWidget()
    widget.show()
    sys.exit(app.exec_())