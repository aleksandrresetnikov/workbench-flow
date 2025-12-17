# Main Screen
# Temporary main screen after successful authorization

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Color constants
PRIMARY_COLOR = "#1D3755"
WHITE_COLOR = "#FFFFFF"
MUTED_COLOR = "#D1E9FF"

class MainScreen(QWidget):
    """Main screen showing user information and logout button"""
    logout_requested = Signal()

    def __init__(self, username: str):
        super().__init__()
        self.username = username
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Card frame
        card = QFrame()
        card.setFixedSize(400, 300)
        card.setStyleSheet(f"""
            background-color: {PRIMARY_COLOR};
            border-radius: 15px;
            padding: 20px;
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(20)

        # Header
        header = QLabel("Welcome to the Application")
        header.setStyleSheet(f"""
            color: {WHITE_COLOR};
            font-size: 24px;
            font-weight: bold;
        """)
        card_layout.addWidget(header)

        # User info
        user_label = QLabel(f"Logged in as: {self.username}")
        user_label.setStyleSheet(f"""
            color: {WHITE_COLOR};
            font-size: 18px;
        """)
        card_layout.addWidget(user_label)

        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.setStyleSheet(f"""
            background-color: {WHITE_COLOR};
            color: {PRIMARY_COLOR};
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
        """)
        logout_button.setFixedHeight(50)
        logout_button.clicked.connect(self.handle_logout)
        card_layout.addWidget(logout_button)

        layout.addWidget(card)

    def handle_logout(self):
        """Handle logout button click"""
        print(f"Logout requested for user: {self.username}")
        self.logout_requested.emit()