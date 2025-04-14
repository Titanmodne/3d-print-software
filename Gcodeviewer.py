import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QSlider, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
import numpy as np

class GCodeViewer(QOpenGLWidget):
    def __init__(self, parent=None):
        try:
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
            self.last_point = None
            self.initialized = False
            print("GCodeViewer initialized")
        except Exception as e:
            print(f"Error in GCodeViewer.__init__: {e}")
            raise

    def initializeGL(self):
        try:
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            glClearColor(1.0, 0.65, 0.65, 1.0)
            glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 10.0, 1.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
            glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
            glEnable(GL_NORMALIZE)
            self.initialized = True
            print("OpenGL initialized")
        except Exception as e:
            print(f"Error in initializeGL: {e}")
            self.initialized = False

    def resizeGL(self, width, height):
        if not self.initialized:
            return
        try:
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            aspect = width / height
            glFrustum(-aspect, aspect, -1.0, 1.0, 1.0, 1000.0)
            glMatrixMode(GL_MODELVIEW)
        except Exception as e:
            print(f"Error in resizeGL: {e}")

    def paintGL(self):
        if not self.initialized:
            return
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()

            glTranslatef(0.0, 0.0, -self.camera_distance)
            glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
            glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
            glTranslatef(-self.view_center_x, -self.view_center_y, -self.view_center_z)
            glScalef(self.scale, self.scale, self.scale)

            glBegin(GL_LINES)
            points_drawn = 0
            self.last_point = None
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
                    self.last_point = end
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
        except Exception as e:
            print(f"Error in paintGL: {e}")

    def mousePressEvent(self, event):
        if not self.initialized:
            return
        try:
            self.last_pos = event.position().toPoint()
        except Exception as e:
            print(f"Error in mousePressEvent: {e}")

    def mouseMoveEvent(self, event):
        if not self.initialized or self.last_pos is None:
            return
        try:
            dx = event.position().x() - self.last_pos.x()
            dy = event.position().y() - self.last_pos.y()
            if event.buttons() & Qt.MouseButton.LeftButton:
                self.view_center_x -= dx * 0.5 / self.scale
                self.view_center_y += dy * 0.5 / self.scale
            elif event.buttons() & Qt.MouseButton.RightButton:
                self.rotation_x += dy * 0.5
                self.rotation_y += dx * 0.5
            self.last_pos = event.position().toPoint()
            self.update()
        except Exception as e:
            print(f"Error in mouseMoveEvent: {e}")

    def wheelEvent(self, event):
        if not self.initialized:
            return
        try:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:  # 修复为正确修饰符
                delta = event.angleDelta().y() // 120
                new_value = max(0, min(self.total_points, self.progress + delta * 100))
                self.parent().progress_slider.setBmpValue(new_value)
            else:
                new_scale = self.scale + event.angleDelta().y() / 1200.0
                self.scale = max(0.01, min(100.0, new_scale))
                print(f"Scale adjusted to: {self.scale}")
            self.update()
        except Exception as e:
            print(f"Error in wheelEvent: {e}")

    def load_gcode(self, file_path):
        if not self.initialized:
            print("OpenGL not initialized, skipping load")
            return
        try:
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

                self.parent().progress_slider.setRange(0, self.total_points)
                self.parent().progress_slider.setValue(0)
                self.progress = 0
                self.parent().update_display()

                print(f"Loaded {len(self.paths)} paths, total points: {self.total_points}, plane size: {self.plane_size}")
                print(f"Initial view center: X={self.view_center_x}, Y={self.view_center_y}, Z={self.view_center_z}")
                print(f"Max dimension: {max_dim}, Camera distance: {self.camera_distance}")
            self.update()
        except Exception as e:
            print(f"Error in load_gcode: {e}")

    def set_progress(self, value):
        if not self.initialized:
            return
        try:
            self.progress = value
            self.parent().update_display()
        except Exception as e:
            print(f"Error in set_progress: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("G-Code Viewer")
            self.resize(800, 600)
            self.gl_widget = GCodeViewer(self)
            self.setCentralWidget(self.gl_widget)

            self.open_button = QPushButton("打开 G-Code 文件", self)
            self.open_button.setGeometry(10, 10, 120, 30)
            self.open_button.clicked.connect(self.open_file)

            self.progress_slider = QSlider(Qt.Orientation.Horizontal, self)
            self.progress_slider.setGeometry(140, 10, 200, 30)
            self.progress_slider.valueChanged.connect(self.gl_widget.set_progress)

            self.point_label = QLabel("Point: 0 / 0", self)
            self.point_label.setGeometry(350, 10, 100, 30)

            self.coord_label = QLabel("X: 0.00, Y: 0.00, Z: 0.00", self)
            self.coord_label.setGeometry(10, self.height() - 40, 150, 30)
            print("MainWindow initialized")
        except Exception as e:
            print(f"Error in MainWindow.__init__: {e}")
            raise

    def update_display(self):
        try:
            self.point_label.setText(f"Point: {self.gl_widget.progress} / {self.gl_widget.total_points}")
            if self.gl_widget.last_point:
                coords = f"X: {self.gl_widget.last_point['X']:.2f}, Y: {self.gl_widget.last_point['Y']:.2f}, Z: {self.gl_widget.last_point['Z']:.2f}"
                self.coord_label.setText(coords)
            else:
                self.coord_label.setText("X: 0.00, Y: 0.00, Z: 0.00")
            self.gl_widget.update()
        except Exception as e:
            print(f"Error in update_display: {e}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.coord_label.setGeometry(10, self.height() - 40, 150, 30)

    def open_file(self):
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "打开 G-Code 文件", "", "G-Code Files (*.gcode)")
            if file_name:
                self.gl_widget.load_gcode(file_name)
        except Exception as e:
            print(f"Error in open_file: {e}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error in main: {e}")