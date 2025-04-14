import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGroupBox, QFormLayout, QLabel,
    QDoubleSpinBox, QSpinBox, QHBoxLayout, QVBoxLayout
)

# 自定义坐标输入控件（用于XYZ坐标）
class CoordinateInput(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        self.x = QDoubleSpinBox()
        self.x.setRange(-1000, 1000)
        self.x.setDecimals(3)  # 修改为3位小数
        self.x.setSuffix(" mm")
        self.y = QDoubleSpinBox()
        self.y.setRange(-1000, 1000)
        self.y.setDecimals(3)  # 修改为3位小数
        self.y.setSuffix(" mm")
        self.z = QDoubleSpinBox()
        self.z.setRange(-1000, 1000)
        self.z.setDecimals(3)  # 修改为3位小数
        self.z.setSuffix(" mm")

        layout.addWidget(QLabel("X:"))
        layout.addWidget(self.x)
        layout.addWidget(QLabel("Y:"))
        layout.addWidget(self.y)
        layout.addWidget(QLabel("Z:"))
        layout.addWidget(self.z)
        self.setLayout(layout)

    def get_values(self):
        """返回 XYZ 坐标值作为一个字典，保留三位小数"""
        return {
            'x': f"{self.x.value():.3f}",
            'y': f"{self.y.value():.3f}",
            'z': f"{self.z.value():.3f}",
        }

    def set_values(self, values):
        """根据传入的字典设置 XYZ 坐标值，提供默认值并处理异常"""
        try:
            self.x.setValue(float(values.get('x', '0.0')))
            self.y.setValue(float(values.get('y', '0.0')))
            self.z.setValue(float(values.get('z', '0.0')))
        except ValueError:
            self.x.setValue(0.0)
            self.y.setValue(0.0)
            self.z.setValue(0.0)

# 主窗口
class DeviceSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设备设置")

        # 主布局（垂直排列）
        main_layout = QVBoxLayout()

        # 三坐标打印机组
        three_axis_group = QGroupBox("三坐标打印机")
        three_axis_layout = QFormLayout()

        self.three_start_point = CoordinateInput()
        three_axis_layout.addRow("打印起始点:", self.three_start_point)

        self.three_t0_to_t1 = CoordinateInput()
        three_axis_layout.addRow("T0相对于T1的位置:", self.three_t0_to_t1)

        self.three_cut_length = QDoubleSpinBox()
        self.three_cut_length.setRange(0, 1000)
        self.three_cut_length.setDecimals(3)  # 修改为3位小数
        self.three_cut_length.setSuffix(" mm")
        three_axis_layout.addRow("剪断长度:", self.three_cut_length)

        self.three_pre_feed_length = QDoubleSpinBox()
        self.three_pre_feed_length.setRange(0, 1000)
        self.three_pre_feed_length.setDecimals(3)  # 修改为3位小数
        self.three_pre_feed_length.setSuffix(" mm")
        three_axis_layout.addRow("预送丝长度:", self.three_pre_feed_length)

        self.three_short_distance = QDoubleSpinBox()
        self.three_short_distance.setRange(0, 1000)
        self.three_short_distance.setDecimals(3)  # 修改为3位小数
        self.three_short_distance.setSuffix(" mm")
        three_axis_layout.addRow("短距离判据:", self.three_short_distance)

        three_axis_group.setLayout(three_axis_layout)
        main_layout.addWidget(three_axis_group)

        # 多自由度打印机组
        multi_axis_group = QGroupBox("多自由度打印机")
        multi_axis_layout = QFormLayout()

        self.multi_start_point = CoordinateInput()
        multi_axis_layout.addRow("打印起始点:", self.multi_start_point)

        self.multi_t0_to_t1 = CoordinateInput()
        multi_axis_layout.addRow("T0相对于T1的位置:", self.multi_t0_to_t1)

        self.multi_cut_length = QDoubleSpinBox()
        self.multi_cut_length.setRange(0, 1000)
        self.multi_cut_length.setDecimals(3)  # 修改为3位小数
        self.multi_cut_length.setSuffix(" mm")
        multi_axis_layout.addRow("剪断长度:", self.multi_cut_length)

        self.multi_pre_feed_length = QDoubleSpinBox()
        self.multi_pre_feed_length.setRange(0, 1000)
        self.multi_pre_feed_length.setDecimals(3)  # 修改为3位小数
        self.multi_pre_feed_length.setSuffix(" mm")
        multi_axis_layout.addRow("预送丝长度:", self.multi_pre_feed_length)

        self.multi_short_distance = QDoubleSpinBox()
        self.multi_short_distance.setRange(0, 1000)
        self.multi_short_distance.setDecimals(3)  # 修改为3位小数
        self.multi_short_distance.setSuffix(" mm")
        multi_axis_layout.addRow("短距离判据:", self.multi_short_distance)

        # 用户坐标系输入框
        self.user_coordinate_value = QSpinBox()
        self.user_coordinate_value.setRange(0, 1000)
        multi_axis_layout.addRow("用户坐标系:", self.user_coordinate_value)

        # 工具坐标系输入框
        self.tool_coordinate_value = QSpinBox()
        self.tool_coordinate_value.setRange(0, 1000)
        multi_axis_layout.addRow("工具坐标系:", self.tool_coordinate_value)

        multi_axis_group.setLayout(multi_axis_layout)
        main_layout.addWidget(multi_axis_group)

        # 设置主布局
        self.setLayout(main_layout)

    def get_config(self):
        """返回设备设置的配置字典，浮点数保留三位小数"""
        return {
            'three_start_point': self.three_start_point.get_values(),
            'three_t0_to_t1': self.three_t0_to_t1.get_values(),
            'three_cut_length': f"{self.three_cut_length.value():.3f}",
            'three_pre_feed_length': f"{self.three_pre_feed_length.value():.3f}",
            'three_short_distance': f"{self.three_short_distance.value():.3f}",
            'multi_start_point': self.multi_start_point.get_values(),
            'multi_t0_to_t1': self.multi_t0_to_t1.get_values(),
            'multi_cut_length': f"{self.multi_cut_length.value():.3f}",
            'multi_pre_feed_length': f"{self.multi_pre_feed_length.value():.3f}",
            'multi_short_distance': f"{self.multi_short_distance.value():.3f}",
            'user_coordinate_value': self.user_coordinate_value.value(),
            'tool_coordinate_value': self.tool_coordinate_value.value(),
        }

    def set_config(self, config):
        """从配置字典加载设备设置，处理字符串格式的浮点数"""
        self.three_start_point.set_values(config.get('three_start_point', {'x': '0.0', 'y': '0.0', 'z': '0.0'}))
        self.three_t0_to_t1.set_values(config.get('three_t0_to_t1', {'x': '0.0', 'y': '0.0', 'z': '0.0'}))
        try:
            self.three_cut_length.setValue(float(config.get('three_cut_length', '0.0')))
            self.three_pre_feed_length.setValue(float(config.get('three_pre_feed_length', '0.0')))
            self.three_short_distance.setValue(float(config.get('three_short_distance', '0.0')))
            self.multi_start_point.set_values(config.get('multi_start_point', {'x': '0.0', 'y': '0.0', 'z': '0.0'}))
            self.multi_t0_to_t1.set_values(config.get('multi_t0_to_t1', {'x': '0.0', 'y': '0.0', 'z': '0.0'}))
            self.multi_cut_length.setValue(float(config.get('multi_cut_length', '0.0')))
            self.multi_pre_feed_length.setValue(float(config.get('multi_pre_feed_length', '0.0')))
            self.multi_short_distance.setValue(float(config.get('multi_short_distance', '0.0')))
        except ValueError:
            self.three_cut_length.setValue(0.0)
            self.three_pre_feed_length.setValue(0.0)
            self.three_short_distance.setValue(0.0)
            self.multi_cut_length.setValue(0.0)
            self.multi_pre_feed_length.setValue(0.0)
            self.multi_short_distance.setValue(0.0)
        self.user_coordinate_value.setValue(config.get('user_coordinate_value', 0))
        self.tool_coordinate_value.setValue(config.get('tool_coordinate_value', 0))

# 程序入口（保持不变）
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = DeviceSettingsWidget()
    widget.show()
    sys.exit(app.exec_())