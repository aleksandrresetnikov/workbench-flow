# Button Components
# Reusable button components

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class PrimaryButton(QPushButton):
    """Primary button with dark blue background"""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("PrimaryButton")
        self.setCursor(Qt.PointingHandCursor)
        # Explicitly set styles to ensure they're applied
        self.setStyleSheet("""
            QPushButton#PrimaryButton {
                background-color: #1D3755;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 14px 24px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#PrimaryButton:hover {
                background-color: #2A4A6B;
            }
            QPushButton#PrimaryButton:pressed {
                background-color: #152A42;
            }
        """)

class SecondaryButton(QPushButton):
    """Secondary button with transparent background"""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setObjectName("SecondaryButton")
        self.setCursor(Qt.PointingHandCursor)

class CreateProjectButton(QPushButton):
    """Create project button with blue background"""
    def __init__(self, text: str = "+ Создать проект", parent=None):
        super().__init__(text, parent)
        self.setObjectName("CreateProjectButton")
        self.setCursor(Qt.PointingHandCursor)

class EyeButton(QPushButton):
    """Eye icon button for password visibility toggle"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EyeButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(24, 24)
        self.setIconSize(self.size())
        self._is_visible = False
        self._update_icon()
    
    def _update_icon(self):
        # Simple text-based icon (can be replaced with actual icon)
        self.setText("👁" if not self._is_visible else "👁‍🗨")
    
    def toggle(self):
        """Toggle password visibility state"""
        self._is_visible = not self._is_visible
        self._update_icon()
        return self._is_visible

