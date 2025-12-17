# Main Application
# Handles the application startup, navigation, and authentication flow

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import QTimer, QThread, Signal

from services import auth_service
from ui.components import LoadingOverlay
from ui.project_screen import ProjectScreen
from ui.auth_screens import LoginScreen, RegistrationScreen, OTPConfirmationScreen
from ui.main_screen import MainScreen

class LoginWorker(QThread):
    """Фоновый поток для выполнения логина и загрузки профиля пользователя."""

    finished_with_result = Signal(bool, str)

    def __init__(self, auth_service, email: str, password: str):
        super().__init__()
        self._auth_service = auth_service
        self._email = email
        self._password = password

    def run(self):
        try:
            if not self._auth_service.login(self._email, self._password):
                self.finished_with_result.emit(False, "Неверный email или пароль. Попробуйте снова.")
                return

            if not self._auth_service.fetch_current_user():
                self.finished_with_result.emit(
                    False, "Не удалось получить информацию о пользователе. Попробуйте снова."
                )
                return

            self.finished_with_result.emit(True, "")
        except Exception as exc:  # на всякий случай
            self.finished_with_result.emit(False, str(exc))


class AuthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workbench Flow")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize services
        self.auth_service = auth_service

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
        self.main_screen = None
        self.project_screen = None
        self._login_worker: LoginWorker | None = None

        # Loading overlay for auth operations
        self.loading_overlay = LoadingOverlay(self, "Входим в аккаунт")

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
        if self.auth_service.current_user:
            self.main_screen = MainScreen(self.auth_service)
            self.main_screen.logout_requested.connect(self.handle_logout)
            self.main_screen.project_open_requested.connect(self.open_project)

            # Add main screen to stacked widget
            self.stacked_widget.addWidget(self.main_screen)
            self.stacked_widget.setCurrentWidget(self.main_screen)

    def open_project(self, project):
        """Open selected project screen."""
        self.project_screen = ProjectScreen(project, self.auth_service)
        self.project_screen.back_requested.connect(self._close_project_screen)
        self.stacked_widget.addWidget(self.project_screen)
        self.stacked_widget.setCurrentWidget(self.project_screen)

    def _close_project_screen(self):
        """Return from project screen back to main screen."""
        if self.project_screen is not None:
            self.stacked_widget.setCurrentWidget(self.main_screen)

    def handle_login(self):
        """Handle login attempt"""
        email = self.login_screen.email_input.text()
        password = self.login_screen.password_input.text()

        self.login_screen.clear_error()
        # Показать оверлей и запустить фоновый поток
        self.loading_overlay.show()

        # Остановить предыдущий поток, если он ещё работает
        if self._login_worker is not None and self._login_worker.isRunning():
            self._login_worker.terminate()

        self._login_worker = LoginWorker(self.auth_service, email, password)
        self._login_worker.finished_with_result.connect(self._on_login_finished)
        self._login_worker.finished.connect(self.loading_overlay.hide)
        self._login_worker.start()

    def _on_login_finished(self, success: bool, message: str):
        """Handle login result from background worker."""
        if success:
            self.show_main_screen()
        else:
            if message:
                self.login_screen.show_error(message)
            print("Login failed:", message)

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