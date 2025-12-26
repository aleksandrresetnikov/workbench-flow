# Input Components
# Reusable input field components

from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from .buttons import EyeButton

class PasswordInput(QWidget):
    """Password input with eye icon for visibility toggle"""
    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.setup_ui(placeholder)
    
    def setup_ui(self, placeholder: str):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.input = QLineEdit()
        self.input.setObjectName("PasswordInput")
        self.input.setPlaceholderText(placeholder)
        self.input.setEchoMode(QLineEdit.Password)
        self.input.setFixedHeight(50)
        layout.addWidget(self.input)
        
        self.eye_button = EyeButton(self)
        self.eye_button.clicked.connect(self.toggle_visibility)
        self.eye_button.setFixedSize(30, 30)
        layout.addWidget(self.eye_button)
        layout.setAlignment(self.eye_button, Qt.AlignRight | Qt.AlignVCenter)
    
    def toggle_visibility(self):
        """Toggle password visibility"""
        is_visible = self.eye_button.toggle()
        self.input.setEchoMode(QLineEdit.Normal if is_visible else QLineEdit.Password)
    
    def text(self) -> str:
        """Get password text"""
        return self.input.text()
    
    def setText(self, text: str):
        """Set password text"""
        self.input.setText(text)
    
    def clear(self):
        """Clear password text"""
        self.input.clear()

class OTPInput(QLineEdit):
    """OTP input field with single character"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OtpInput")
        self.setMaxLength(1)
        self.setAlignment(Qt.AlignCenter)
        # Size tuned to theme to avoid overlap and leave spacing room
        self.setFixedSize(56, 64)
        # Only allow single digits
        self.setValidator(QIntValidator(0, 9, self))

    def keyPressEvent(self, event):
        """Only allow digits and handle navigation cleanly (input handles focus movement)"""
        if event.text().isdigit():
            # Insert digit
            super().keyPressEvent(event)
            # Move focus to next field after digit input
            self.focusNextChild()
        elif event.key() in [Qt.Key_Backspace, Qt.Key_Delete]:
            if not self.text():
                # Move to previous field if backspace on empty field
                self.focusPreviousChild()
            else:
                super().keyPressEvent(event)
        elif event.key() == Qt.Key_Left:
            self.focusPreviousChild()
        elif event.key() == Qt.Key_Right:
            self.focusNextChild()
