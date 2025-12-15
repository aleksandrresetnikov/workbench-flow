from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QPushButton, QLabel, QHBoxLayout, QStatusBar)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon

class TestWindow(QMainWindow):
    # Сигналы (события)
    button_clicked = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
    
    def init_ui(self):
        # Основные настройки окна
        self.setWindowTitle("Мое приложение")
        self.setGeometry(100, 100, 800, 600)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создание layout
        main_layout = QVBoxLayout()
        
        # Виджеты
        self.label = QLabel("Добро пожаловать!")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.button = QPushButton("Нажми меня!")
        self.button.clicked.connect(self.on_button_clicked)
        
        # Добавление виджетов в layout
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.button)
        
        # Установка layout
        central_widget.setLayout(main_layout)
    
    def setup_menu(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("&Файл")
        
        new_action = QAction("&Новый", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def setup_toolbar(self):
        """Создание панели инструментов"""
        toolbar = self.addToolBar("Панель инструментов")
        
        new_action = QAction("Новый", self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
    
    def setup_statusbar(self):
        """Создание строки состояния"""
        self.statusBar().showMessage("Готово")
    
    def on_button_clicked(self):
        """Обработчик нажатия кнопки"""
        self.label.setText("Кнопка нажата!")
        self.statusBar().showMessage("Кнопка была нажата", 3000)
        self.button_clicked.emit("button_clicked")
    
    def new_file(self):
        """Создание нового файла"""
        self.label.setText("Создан новый файл")
        self.statusBar().showMessage("Новый файл создан")

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        # Здесь можно добавить сохранение данных
        # или подтверждение выхода
        event.accept()