# Main Application
# Handles the application startup, navigation, and authentication flow

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import QTimer

from services import auth_service
from ui.auth_screens import LoginScreen, RegistrationScreen, OTPConfirmationScreen
from ui.main_screen import MainScreen
from ui.project_screen import ProjectScreen

class AuthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workbench Flow")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize services
        self.auth_service = auth_service

        # Screens cache
        self.main_screen: MainScreen | None = None
        self.project_screens: dict[int, ProjectScreen] = {}

        # Setup UI
        self.setup_ui()

        # Check auth state on startup
        self.check_auth_state()

    def setup_ui(self):
        # Create stacked widget for navigation
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create screens
        self.login_screen = LoginScreen()
        self.registration_screen = RegistrationScreen()

        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.registration_screen)

        # Connect signals
        self.login_screen.login_success.connect(self.handle_login)
        self.login_screen.switch_to_registration.connect(self.show_registration)

        self.registration_screen.registration_success.connect(self.handle_registration)
        self.registration_screen.switch_to_login.connect(self.show_login)

    def check_auth_state(self):
        """Check authentication state on app startup"""
        if self.auth_service.token:
            # Try to fetch current user
            if self.auth_service.fetch_current_user():
                self.show_main_screen()
            else:
                # Token is invalid, show login
                self.show_login()
        else:
            # No token, show login
            self.show_login()

    def show_login(self):
        """Show login screen"""
        self.stacked_widget.setCurrentWidget(self.login_screen)

    def show_registration(self):
        """Show registration screen"""
        self.stacked_widget.setCurrentWidget(self.registration_screen)

    def show_otp_confirmation(self, email: str):
        """Show OTP confirmation screen"""
        self.otp_screen = OTPConfirmationScreen(email)
        self.otp_screen.otp_success.connect(self.handle_otp_confirmation)
        self.otp_screen.resend_otp.connect(self.handle_resend_otp)
        
        # Add OTP screen to stacked widget
        self.stacked_widget.addWidget(self.otp_screen)
        self.stacked_widget.setCurrentWidget(self.otp_screen)

    def show_main_screen(self):
        """Show main screen"""
        if not self.auth_service.current_user:
            return

        if self.main_screen is None:
            self.main_screen = MainScreen(self.auth_service)
            self.main_screen.logout_requested.connect(self.handle_logout)
            self.main_screen.project_open_requested.connect(self.show_project_screen)
            self.stacked_widget.addWidget(self.main_screen)

        self.stacked_widget.setCurrentWidget(self.main_screen)

    def show_project_screen(self, project_id: int):
        """Show individual project screen"""
        if project_id not in self.project_screens:
            project_screen = ProjectScreen(self.auth_service, project_id)
            project_screen.back_requested.connect(self.show_main_screen)
            project_screen.logout_requested.connect(self.handle_logout)
            self.project_screens[project_id] = project_screen
            self.stacked_widget.addWidget(project_screen)

        self.stacked_widget.setCurrentWidget(self.project_screens[project_id])

    def handle_login(self):
        """Handle login attempt"""
        email = self.login_screen.email_input.text()
        password = self.login_screen.password_input.text()
        
        if self.auth_service.login(email, password):
            if self.auth_service.fetch_current_user():
                self.show_main_screen()
            else:
                error_msg = "Не удалось получить информацию о пользователе. Попробуйте снова."
                self.login_screen.show_error(error_msg)
                print("Failed to fetch user after login")
        else:
            error_msg = "Неверный email или пароль. Попробуйте снова."
            self.login_screen.show_error(error_msg)
            print("Login failed")

    def handle_registration(self):
        """Handle registration attempt"""
        email = self.registration_screen.email_input.text()
        password = self.registration_screen.password_input.text()
        
        if not email or not password:
            error_msg = "Пожалуйста, заполните все поля."
            self.registration_screen.show_error(error_msg)
            return
        
        if self.auth_service.register_user(email, email, password):
            # Registration successful, show OTP confirmation
            self.show_otp_confirmation(email)
        else:
            error_msg = "Не удалось зарегистрироваться. Проверьте данные и попробуйте снова."
            self.registration_screen.show_error(error_msg)
            print("Registration failed")

    def handle_otp_confirmation(self):
        """Handle OTP confirmation"""
        otp_code = self.otp_screen.get_otp_code()
        email = self.otp_screen.email
        
        if len(otp_code) != 6:
            print("Please enter all 6 digits")
            return
        
        if self.auth_service.confirm_otp(email, otp_code):
            # OTP confirmation successful, user is now authorized
            if self.auth_service.fetch_current_user():
                self.show_main_screen()
            else:
                print("Failed to fetch user after OTP confirmation")
        else:
            print("OTP confirmation failed")

    def handle_resend_otp(self):
        """Handle OTP resend request"""
        email = self.otp_screen.email
        if self.auth_service.resend_otp(email):
            print("OTP resent successfully")
        else:
            print("Failed to resend OTP")

    def handle_logout(self):
        """Handle logout request"""
        self.auth_service.logout()
        self.show_login()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load and apply global theme
    try:
        import os
        theme_path = os.path.join(os.path.dirname(__file__), "ui", "styles", "theme.qss")
        with open(theme_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Warning: Could not load theme.qss file")
    
    window = AuthApp()
    window.show()
    sys.exit(app.exec())