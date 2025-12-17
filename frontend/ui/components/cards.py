# Card Components
# Reusable card components

from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtCore import Qt

class AuthCard(QFrame):
    """Authentication card with white background"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AuthCard")
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setSpacing(20)

class ModalCard(QFrame):
    """Modal dialog card with white background"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ModalCard")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(20)

