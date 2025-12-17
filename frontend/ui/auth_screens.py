# Authentication Screens
# Contains the UI implementation for login, registration, and OTP confirmation screens

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon

# Color constants
PRIMARY_COLOR = "#1D3755"
WHITE_COLOR = "#FFFFFF"
MUTED_COLOR = "#D1E9FF"

class LoginScreen(QWidget):
    """Login screen with email and password inputs"""
    login_success = Signal()
    switch_to_registration = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Card frame
        card = QFrame()
        card.setFixedSize(400, 400)
        card.setStyleSheet(f"""
            background-color: {PRIMARY_COLOR};
            border-radius: 15px;
            padding: 20px;
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(20)

        # Title
        title = QLabel("Login")
        title.setStyleSheet(f"""
            color: {WHITE_COLOR};
            font-size: 24px;
            font-weight: bold;
        """)
        card_layout.addWidget(title)

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet(f"""
            background-color: {WHITE_COLOR};
            border: 2px solid {MUTED_COLOR};
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        """)
        self.email_input.setFixedHeight(50)
        card_layout.addWidget(self.email_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            background-color: {WHITE_COLOR};
            border: 2px solid {MUTED_COLOR};
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        """)
        self.password_input.setFixedHeight(50)
        card_layout.addWidget(self.password_input)

        # Login button
        login_button = QPushButton("Login")
        login_button.setStyleSheet(f"""
            background-color: {WHITE_COLOR};
            color: {PRIMARY_COLOR};
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
        """)
        login_button.setFixedHeight(50)
        login_button.clicked.connect(self.handle_login)
        card_layout.addWidget(login_button)

        # Registration link
        reg_link = QLabel("<a href='#' style='color: white;'>Create an account</a>")
        reg_link.setAlignment(Qt.AlignCenter)
        reg_link.linkActivated.connect(lambda: self.switch_to_registration.emit())
        card_layout.addWidget(reg_link)

        layout.addWidget(card)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        # Emit login signal with credentials
        # This will be handled by the main application
        print(f"Login attempt: {email}, {password}")
        self.login_success.emit()

class RegistrationScreen(QWidget):
    """Registration screen with email and password inputs"""
    registration_success = Signal()
    switch_to_login = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Card frame
        card = QFrame()
        card.setFixedSize(400, 450)
        card.setStyleSheet(f"""
            background-color: {PRIMARY_COLOR};
            border-radius: 15px;
            padding: 20px;
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(20)

        # Title
        title = QLabel("Create Account")
        title.setStyleSheet(f"""
            color: {WHITE_COLOR};
            font-size: 24px;
            font-weight: bold;
        """)
        card_layout.addWidget(title)

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet(f"""
            background-color: {WHITE_COLOR};
            border: 2px solid {MUTED_COLOR};
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        """)
        self.email_input.setFixedHeight(50)
        card_layout.addWidget(self.email_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(f"""
            background-color: {WHITE_COLOR};
            border: 2px solid {MUTED_COLOR};
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        """)
        self.password_input.setFixedHeight(50)
        card_layout.addWidget(self.password_input)

        # Create account button
        create_button = QPushButton("Create Account")
        create_button.setStyleSheet(f"""
            background-color: {WHITE_COLOR};
            color: {PRIMARY_COLOR};
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
        """)
        create_button.setFixedHeight(50)
        create_button.clicked.connect(self.handle_registration)
        card_layout.addWidget(create_button)

        # Login link
        login_link = QLabel("<a href='#' style='color: white;'>Already have an account? Login</a>")
        login_link.setAlignment(Qt.AlignCenter)
        login_link.linkActivated.connect(lambda: self.switch_to_login.emit())
        card_layout.addWidget(login_link)

        layout.addWidget(card)

    def handle_registration(self):
        email = self.email_input.text()
        password = self.password_input.text()
        # Emit registration signal with credentials
        print(f"Registration attempt: {email}, {password}")
        self.registration_success.emit()

class OTPConfirmationScreen(QWidget):
    """OTP confirmation screen with 6 digit inputs"""
    otp_success = Signal()
    resend_otp = Signal()

    def __init__(self, email: str):
        super().__init__()
        self.email = email
        self.otp_inputs = []
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Card frame
        card = QFrame()
        card.setFixedSize(500, 400)
        card.setStyleSheet(f"""
            background-color: {PRIMARY_COLOR};
            border-radius: 15px;
            padding: 20px;
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)
        card_layout.setSpacing(20)

        # Title
        title = QLabel("OTP Confirmation")
        title.setStyleSheet(f"""
            color: {WHITE_COLOR};
            font-size: 24px;
            font-weight: bold;
        """)
        card_layout.addWidget(title)

        # Description
        description = QLabel(f"A 6-digit OTP has been sent to {self.email}")
        description.setStyleSheet(f"""
            color: {WHITE_COLOR};
            font-size: 16px;
        """)
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(description)

        # OTP inputs container
        otp_container = QHBoxLayout()
        otp_container.setAlignment(Qt.AlignCenter)
        otp_container.setSpacing(10)

        # Create 6 OTP input fields
        for i in range(6):
            otp_input = QLineEdit()
            otp_input.setMaxLength(1)
            otp_input.setAlignment(Qt.AlignCenter)
            otp_input.setStyleSheet(f"""
                background-color: {WHITE_COLOR};
                border: 2px solid {MUTED_COLOR};
                border-radius: 8px;
                padding: 10px;
                font-size: 20px;
                font-weight: bold;
            """)
            otp_input.setFixedSize(50, 60)
            otp_input.textChanged.connect(lambda text, idx=i: self.handle_otp_input(text, idx))
            self.otp_inputs.append(otp_input)
            otp_container.addWidget(otp_input)

        card_layout.addLayout(otp_container)

        # Continue button
        continue_button = QPushButton("Continue")
        continue_button.setStyleSheet(f"""
            background-color: {WHITE_COLOR};
            color: {PRIMARY_COLOR};
            border: none;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
        """)
        continue_button.setFixedHeight(50)
        continue_button.clicked.connect(self.handle_continue)
        card_layout.addWidget(continue_button)

        # Resend OTP button
        resend_button = QPushButton("Resend OTP")
        resend_button.setStyleSheet(f"""
            background-color: transparent;
            color: {WHITE_COLOR};
            border: 1px solid {WHITE_COLOR};
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
        """)
        resend_button.setFixedHeight(50)
        resend_button.clicked.connect(lambda: self.resend_otp.emit())
        card_layout.addWidget(resend_button)

        layout.addWidget(card)

    def handle_otp_input(self, text: str, index: int):
        """Handle OTP input and auto-focus next field"""
        if text and index < 5:
            self.otp_inputs[index + 1].setFocus()

    def handle_continue(self):
        """Handle continue button click"""
        otp_code = "".join([input.text() for input in self.otp_inputs])
        if len(otp_code) == 6:
            print(f"OTP confirmation attempt: {otp_code}")
            self.otp_success.emit()
        else:
            print("Please enter all 6 digits")

    def get_otp_code(self) -> str:
        """Get the complete OTP code"""
        return "".join([input.text() for input in self.otp_inputs])