from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDateEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from services.auth_service import AuthService
from api.projects import projects_api
from api.dtos import ProjectCreateDTO, ProjectDTO
from ui.components import FieldLabel, ModalCard, PrimaryButton


class CreateProjectDialog(QDialog):
    """Диалог создания нового проекта"""

    project_created = Signal(ProjectDTO)

    def __init__(self, auth_service: AuthService, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.setWindowTitle("Новый проект")
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(550)

        title = QLabel("Новый проект")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet(
            "color: #000000; font-size: 24px; font-weight: bold; margin-bottom: 20px;"
        )
        card.layout.addWidget(title)

        name_label = FieldLabel("Наименование")
        card.layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("InputField")
        self.name_input.setPlaceholderText("Введите наименование проекта")
        self.name_input.setFixedHeight(50)
        card.layout.addWidget(self.name_input)

        desc_label = FieldLabel("Описание")
        card.layout.addWidget(desc_label)

        self.desc_input = QTextEdit()
        self.desc_input.setObjectName("TextEdit")
        self.desc_input.setPlaceholderText("Введите описание проекта")
        self.desc_input.setMaximumHeight(100)
        card.layout.addWidget(self.desc_input)

        deadline_label = FieldLabel("Сроки выполнения")
        card.layout.addWidget(deadline_label)

        self.deadline_input = QDateEdit()
        self.deadline_input.setObjectName("DateEdit")
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setFixedHeight(50)
        card.layout.addWidget(self.deadline_input)

        create_button = PrimaryButton("Создать")
        create_button.setFixedHeight(50)
        create_button.clicked.connect(self.accept)
        card.layout.addWidget(create_button)

        layout.addWidget(card)

    def accept(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка валидации", "Наименование проекта обязательно.")
            return

        desc = self.desc_input.toPlainText().strip()

        data = ProjectCreateDTO(Name=name, Description=desc or None)

        try:
            project = projects_api.create_project(data, self.auth_service.token)
            self.project_created.emit(project)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать проект: {e}")


