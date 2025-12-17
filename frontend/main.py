import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader

# Initialize API client
from api.client import api_client

from modules.test_window import TestWindow

def load_stylesheet():
    """Загрузка стилей"""
    if os.path.exists("styles/style.qss"):
        with open("styles/style.qss", "r") as f:
            return f.read()
    return ""

def test_api_connection():
    """Test API connection"""
    try:
        # Test health check endpoint
        response = api_client._make_request("GET", "/health")
        print(f"API Health Check: {response}")
        return True
    except Exception as e:
        print(f"API connection test failed: {e}")
        return False

def main():
    # Инициализация приложения
    app = QApplication(sys.argv)
    
    # Initialize API client with base URL
    api_client = api_client  # This ensures the client is initialized
    
    # Test API connection
    try:
        health = api_client.health_check()
        print(f"API Health Check: {health}")
    except Exception as e:
        print(f"Warning: Could not connect to API server: {e}")
    
    # Загрузка стилей
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # Создание главного окна
    window = TestWindow()
    window.show()
    
    # Запуск цикла событий
    sys.exit(app.exec())

if __name__ == "__main__":
    main()