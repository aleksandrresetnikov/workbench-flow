# Main Application
# Handles the application startup, navigation, and authentication flow

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import QTimer

from services import auth_service
from ui.auth_screens import LoginScreen, RegistrationScreen, OTPConfirmationScreen
from ui.main_screen import MainScreen

class AuthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Authentication App")
        self.setGeometry(100, 100, 800, 600)

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
            username = self.auth_service.current_user.Username
            self.main_screen = MainScreen(username)
            self.main_screen.logout_requested.connect(self.handle_logout)
            
            # Add main screen to stacked widget
            self.stacked_widget.addWidget(self.main_screen)
            self.stacked_widget.setCurrentWidget(self.main_screen)

    def handle_login(self):
        """Handle login attempt"""
        email = self.login_screen.email_input.text()
        password = self.login_screen.password_input.text()
        
        if self.auth_service.login(email, password):
            if self.auth_service.fetch_current_user():
                self.show_main_screen()
            else:
                error_msg = "Failed to fetch user information. Please try again."
                self.login_screen.show_error(error_msg)
                print("Failed to fetch user after login")
        else:
            error_msg = "Invalid username or password. Please try again."
            self.login_screen.show_error(error_msg)
            print("Login failed")

    def handle_registration(self):
        """Handle registration attempt"""
        email = self.registration_screen.email_input.text()
        password = self.registration_screen.password_input.text()
        
        if self.auth_service.register_user(email, email, password):
            # Registration successful, show OTP confirmation
            self.show_otp_confirmation(email)
        else:
            print("Registration failed")

    def handle_otp_confirmation(self):
        """Handle OTP confirmation"""
        otp_code = self.otp_screen.get_otp_code()
        email = self.otp_screen.email
        
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
        with open("ui/styles/theme.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Warning: Could not load theme.qss file")
    
    window = AuthApp()
    window.show()
    sys.exit(app.exec())