import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QFileDialog, QLineEdit, QWidget, \
    QComboBox, QLabel
import qdarkstyle
from reorganization import process_file  # 假设你已经将处理函数保存为 gcode_processor.py


class GCodeProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("G-code 文件处理")
        self.setGeometry(300, 300, 400, 600)  # 扩展窗口大小

        # 创建主界面
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)

        # 创建布局
        layout = QVBoxLayout()

        # 输入和输出文件路径
        self.input_file_edit = QLineEdit(self)
        self.input_file_edit.setPlaceholderText("选择输入文件")
        layout.addWidget(self.input_file_edit)

        self.output_file_edit = QLineEdit(self)
        self.output_file_edit.setPlaceholderText("选择输出文件")
        layout.addWidget(self.output_file_edit)

        # 浏览按钮
        browse_input_button = QPushButton("浏览输入文件", self)
        browse_input_button.clicked.connect(self.select_input_file)
        layout.addWidget(browse_input_button)

        browse_output_button = QPushButton("浏览输出文件", self)
        browse_output_button.clicked.connect(self.select_output_file)
        layout.addWidget(browse_output_button)

        # 显示和编辑 type_map
        self.type_map_comboboxes = {}  # 存储每个TYPE对应的QComboBox

        # 所有的TYPE选项
        type_options = ['FILL', 'WALL-INNER', 'WALL-OUTER', 'SUPPORT', 'SUPPORT-INTERFACE', 'SKIN', 'SKIRT']

        for type_name in type_options:
            label = QLabel(f"{type_name} 对应的 T 值:", self)
            layout.addWidget(label)

            combobox = QComboBox(self)
            combobox.addItem('T0')
            combobox.addItem('T1')
            combobox.setCurrentText('T0' if type_name in ['FILL', 'SKIN', 'SKIRT'] else 'T1')  # 默认值设置
            self.type_map_comboboxes[type_name] = combobox
            layout.addWidget(combobox)

        # 更新按钮
        update_button = QPushButton("更新 T 值", self)
        update_button.clicked.connect(self.update_type_map)
        layout.addWidget(update_button)

        # 开始处理按钮
        process_button = QPushButton("开始处理", self)
        process_button.clicked.connect(self.process_files)
        layout.addWidget(process_button)

        # 设置布局
        self.main_widget.setLayout(layout)

        # 初始化 type_map 字典
        self.type_map = {
            'FILL': 'T0',
            'WALL-INNER': 'T0',
            'WALL-OUTER': 'T1',
            'SUPPORT': 'T1',
            'SUPPORT-INTERFACE': 'T',
            'SKIN': 'T1',
            'SKIRT': 'T1',
        }

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择输入文件", "", "G-code Files (*.gcode)")
        if file_path:
            self.input_file_edit.setText(file_path)

    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "选择输出文件", "", "G-code Files (*.gcode)")
        if file_path:
            self.output_file_edit.setText(file_path)

    def update_type_map(self):
        # 获取所有TYPE对应的T值并更新 type_map
        for type_name, combobox in self.type_map_comboboxes.items():
            selected_t_value = combobox.currentText()
            self.type_map[type_name] = selected_t_value
            print(f"已更新 {type_name} 为 {selected_t_value}")

    def process_files(self):
        input_file = self.input_file_edit.text()
        output_file = self.output_file_edit.text()

        # 调用处理函数
        process_file(input_file, output_file, self.type_map)

        # 提示处理完成
        print(f"文件处理完毕，已保存为 {output_file}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置QDarkStyle主题
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    window = GCodeProcessorApp()
    window.show()

    sys.exit(app.exec_())
