# Authentication Screens
# Contains the UI implementation for login, registration, and OTP confirmation screens

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
)
from PySide6.QtCore import Qt, Signal

from ui.components import (
    AuthCard, PrimaryButton, SecondaryButton,
    TitleLabel, FieldLabel, DescriptionLabel, LinkLabel,
    PasswordInput, OTPInput
)

class LoginScreen(QWidget):
    """Login screen with email and password inputs"""
    login_success = Signal()
    switch_to_registration = Signal()
    forgot_password = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # Main layout with dark blue background
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Card frame
        card = AuthCard()
        card.setFixedWidth(450)

        # Title
        title = TitleLabel("Вход в аккаунт")
        card.layout.addWidget(title)

        # Email input
        email_label = FieldLabel("Почта")
        card.layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setObjectName("InputField")
        self.email_input.setPlaceholderText("Введите email")
        self.email_input.setFixedHeight(50)
        card.layout.addWidget(self.email_input)

        # Password input with label and forgot password link
        password_header = QHBoxLayout()
        password_label = FieldLabel("Пароль")
        password_header.addWidget(password_label)
        password_header.addStretch()
        
        forgot_link = LinkLabel("<a href='#' style='color: #4A90E2; text-decoration: none;'>Забыли пароль?</a>")
        forgot_link.linkActivated.connect(lambda: self.forgot_password.emit())
        password_header.addWidget(forgot_link)
        
        password_widget = QWidget()
        password_widget.setLayout(password_header)
        password_widget.setStyleSheet("background-color: transparent;")
        card.layout.addWidget(password_widget)
        
        self.password_input = PasswordInput("Введите пароль")
        self.password_input.setFixedHeight(50)
        card.layout.addWidget(self.password_input)

        # Login button
        login_button = PrimaryButton("Вход")
        login_button.setFixedHeight(50)
        login_button.clicked.connect(self.handle_login)
        card.layout.addWidget(login_button)

        # Error label (initially hidden)
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)
        card.layout.addWidget(self.error_label)

        # Registration link
        reg_text = "Еще нет аккаунта? <a href='#' style='color: #4A90E2; text-decoration: none;'>Регистрация</a>"
        reg_link = LinkLabel(reg_text)
        reg_link.linkActivated.connect(lambda: self.switch_to_registration.emit())
        card.layout.addWidget(reg_link)

        layout.addWidget(card)

    def show_error(self, message: str):
        """Show error message to user"""
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def clear_error(self):
        """Clear error message"""
        self.error_label.setVisible(False)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        print(f"Login attempt: {email}")
        self.clear_error()
        self.login_success.emit()


class RegistrationScreen(QWidget):
    """Registration screen with email and password inputs"""
    registration_success = Signal()
    switch_to_login = Signal()

    def __init__(self):
        super().__init__()
        self.error_label = None
        self.setup_ui()

    def setup_ui(self):
        # Main layout with dark blue background
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Card frame
        card = AuthCard()
        card.setFixedWidth(450)

        # Title
        title = TitleLabel("Создать аккаунт")
        card.layout.addWidget(title)

        # Email input
        email_label = FieldLabel("Почта")
        card.layout.addWidget(email_label)
        
        self.email_input = QLineEdit()
        self.email_input.setObjectName("InputField")
        self.email_input.setPlaceholderText("Введите email")
        self.email_input.setFixedHeight(50)
        card.layout.addWidget(self.email_input)

        # Password input
        password_label = FieldLabel("Пароль")
        card.layout.addWidget(password_label)
        
        self.password_input = PasswordInput("Введите пароль")
        self.password_input.setFixedHeight(50)
        card.layout.addWidget(self.password_input)

        # Create account button
        create_button = PrimaryButton("Создать аккаунт")
        create_button.setFixedHeight(50)
        create_button.clicked.connect(self.handle_registration)
        card.layout.addWidget(create_button)

        # Error label (initially hidden)
        self.error_label = QLabel("")
        self.error_label.setObjectName("ErrorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setVisible(False)
        card.layout.addWidget(self.error_label)

        # Login link
        login_text = "Уже есть аккаунт? <a href='#' style='color: #4A90E2; text-decoration: none;'>Вход</a>"
        login_link = LinkLabel(login_text)
        login_link.linkActivated.connect(lambda: self.switch_to_login.emit())
        card.layout.addWidget(login_link)

        layout.addWidget(card)

    def show_error(self, message: str):
        """Show error message to user"""
        if self.error_label:
            self.error_label.setText(message)
            self.error_label.setVisible(True)

    def clear_error(self):
        """Clear error message"""
        if self.error_label:
            self.error_label.setVisible(False)

    def handle_registration(self):
        email = self.email_input.text()
        password = self.password_input.text()
        print(f"Registration attempt: {email}")
        self.clear_error()
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
        # Main layout with dark blue background
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Card frame
        card = AuthCard()
        card.setFixedWidth(500)

        # Title
        title = TitleLabel("Подтверждение эл. почты")
        card.layout.addWidget(title)

        # Description
        description_text = f"На почту <b>{self.email}</b> было отправлено письмо с 6-ти значным кодом"
        description = DescriptionLabel(description_text)
        card.layout.addWidget(description)

        # OTP inputs container
        otp_container = QHBoxLayout()
        otp_container.setAlignment(Qt.AlignCenter)
        otp_container.setSpacing(15)

        # Create 6 OTP input fields
        for i in range(6):
            otp_input = OTPInput()
            otp_input.textChanged.connect(lambda text, idx=i: self.handle_otp_input(text, idx))
            self.otp_inputs.append(otp_input)
            otp_container.addWidget(otp_input)

        otp_widget = QWidget()
        otp_widget.setLayout(otp_container)
        otp_widget.setStyleSheet("background-color: transparent;")
        card.layout.addWidget(otp_widget)

        # Continue button
        continue_button = PrimaryButton("Продолжить")
        continue_button.setFixedHeight(50)
        continue_button.clicked.connect(self.handle_continue)
        card.layout.addWidget(continue_button)

        # Resend OTP link
        resend_text = "<a href='#' style='color: #666666; text-decoration: none;'>Отправить otp код еще раз</a>"
        resend_link = LinkLabel(resend_text)
        resend_link.linkActivated.connect(lambda: self.resend_otp.emit())
        card.layout.addWidget(resend_link)

        layout.addWidget(card)

    def handle_otp_input(self, text: str, index: int):
        """Handle OTP input and auto-focus next field"""
        if text and index < 5:
            self.otp_inputs[index + 1].setFocus()
        elif not text and index > 0:
            # Allow backspace to move to previous field
            pass

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
