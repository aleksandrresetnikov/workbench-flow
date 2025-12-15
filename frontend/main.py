import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

from modules.test_window import TestWindow

def load_stylesheet():
    """Загрузка стилей"""
    if os.path.exists("styles/style.qss"):
        with open("styles/style.qss", "r") as f:
            return f.read()
    return ""

def main():
    # Инициализация приложения
    app = QApplication(sys.argv)
    
    # Загрузка стилей
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)
    
    # Создание главного окна
    window = TestWindow()
    window.show()
    
    # Запуск цикла событий
    sys.exit(app.exec())

if __name__ == "__main__":
    main()