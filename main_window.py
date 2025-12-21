from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import os

from lab2 import ImagePathIterator

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataset Viewer — Лабораторная работа 5")
        self.resize(1100, 800)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(QtCore.Qt.AlignCenter)

        self.image_label = QtWidgets.QLabel("Идёт поиск датасета из lab2...")
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setStyleSheet("font-size: 18px; color: #444;")
        self.image_label.setWordWrap(True)

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

        btn_layout = QtWidgets.QHBoxLayout()

        self.btn_prev = QtWidgets.QPushButton("← Предыдущее изображение")
        self.btn_prev.clicked.connect(self.show_previous_image)
        self.btn_prev.setEnabled(False)  
        btn_layout.addWidget(self.btn_prev)

        self.btn_next = QtWidgets.QPushButton("Следующее изображение →")
        self.btn_next.clicked.connect(self.show_next_image)
        self.btn_next.setEnabled(False)
        btn_layout.addWidget(self.btn_next)

        self.btn_choose = QtWidgets.QPushButton("Выбрать другой датасет")
        self.btn_choose.clicked.connect(self.choose_dataset)
        btn_layout.addWidget(self.btn_choose)

        layout.addLayout(btn_layout)

        self.iterator = None
        self.image_paths_list = [] 
        self.current_index = -1

        self.auto_load_from_lab2()

    def auto_load_from_lab2(self):
        lab2_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lab2'))

        if not os.path.exists(lab2_path):
            self.image_label.setText("❌ Папка 'lab2' не найдена!\nУбедитесь, что она рядом с 'lab5'.")
            return

        loaded = False

        for item in os.listdir(lab2_path):
            if item.lower().endswith('.csv'):
                csv_path = os.path.join(lab2_path, item)
                if self.load_dataset(csv_path):
                    self.image_label.setText(f"✅ Загружено из аннотации:\n{item}")
                    loaded = True
                    break

        if not loaded:
            for item in os.listdir(lab2_path):
                item_path = os.path.join(lab2_path, item)
                if os.path.isdir(item_path):
                    images = [f for f in os.listdir(item_path)
                              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
                    if images:
                        if self.load_dataset(item_path):
                            self.image_label.setText(f"✅ Загружено из папки:\n{item} ({len(images)} шт.)")
                            loaded = True
                            break

        if not loaded:
            self.image_label.setText("⚠️ Датасет не найден в lab2.\nНажмите 'Выбрать другой датасет'.")

    def load_dataset(self, path):
        try:

            temp_iterator = ImagePathIterator(path)
            self.image_paths_list = list(temp_iterator)
            
            if not self.image_paths_list:
                QtWidgets.QMessageBox.warning(self, "Пусто", "В датасете нет изображений.")
                return False

            self.current_index = 0
            self.show_current_image()

            self.btn_prev.setEnabled(False)  
            self.btn_next.setEnabled(len(self.image_paths_list) > 1)
            return True
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить:\n{str(e)}")
            return False

    def show_current_image(self):
        if not (0 <= self.current_index < len(self.image_paths_list)):
            return

        image_path = self.image_paths_list[self.current_index]

        pixmap = QtGui.QPixmap(image_path)
        if pixmap.isNull():
            self.image_label.setText(f"Ошибка загрузки:\n{os.path.basename(image_path)}")
            return

        view_size = self.scroll_area.viewport().size()
        scaled = pixmap.scaled(view_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled)

        self.setWindowTitle(f"Dataset Viewer — {os.path.basename(image_path)} ({self.current_index + 1}/{len(self.image_paths_list)})")

        # Управление кнопками
        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < len(self.image_paths_list) - 1)

    def show_next_image(self):
        if self.current_index < len(self.image_paths_list) - 1:
            self.current_index += 1
            self.show_current_image()

    def show_previous_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_image()

    def choose_dataset(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Выбрать CSV", "", "CSV (*.csv)")
        if not path:
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выбрать папку с изображениями")
        if path and self.load_dataset(path):
            self.image_label.setText(f"Загружено вручную:\n{os.path.basename(path)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())