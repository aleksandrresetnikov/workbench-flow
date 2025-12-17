# Label Components
# Reusable label components

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class TitleLabel(QLabel):
    """Title label with bold black text"""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("TitleLabel")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: transparent;")

class FieldLabel(QLabel):
    """Field label for form inputs"""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("FieldLabel")
        self.setStyleSheet("background-color: transparent;")

class DescriptionLabel(QLabel):
    """Description label with gray text"""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("DescriptionLabel")
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: transparent;")

class LinkLabel(QLabel):
    """Link label with clickable text"""
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("LinkLabel")
        self.setAlignment(Qt.AlignCenter)
        self.setOpenExternalLinks(False)
        self.setStyleSheet("background-color: transparent;")

