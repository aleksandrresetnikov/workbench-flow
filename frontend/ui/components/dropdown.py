# Dropdown Component
# Dropdown menu component

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal

class UserDropdown(QFrame):
    """Dropdown menu for user actions"""
    logout_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UserDropdown")
        self.setFixedWidth(180)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Logout button
        logout_btn = QPushButton("Выход")
        logout_btn.setObjectName("DropdownButton")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

