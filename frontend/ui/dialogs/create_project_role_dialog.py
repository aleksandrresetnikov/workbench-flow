from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QHBoxLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from services.auth_service import AuthService
from api.projects import projects_api
from api.dtos import ProjectRoleCreateDTO, ProjectRoleDTO
from ui.components import ModalCard, FieldLabel, PrimaryButton, SecondaryButton


class CreateProjectRoleDialog(QDialog):
    """Вложенный диалог для создания роли в проекте."""

    role_created = Signal(ProjectRoleDTO)

    def __init__(self, auth_service: AuthService, project_id: int, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.project_id = project_id

        self.setWindowTitle("Новая роль проекта")
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setAlignment(Qt.AlignCenter)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(480)

        title = QLabel("Новая роль")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet(
            "color: #000000; font-size: 20px; font-weight: bold; margin-bottom: 12px;"
        )
        card.layout.addWidget(title)

        subtitle = QLabel(
            "Создайте роль, которую затем можно будет назначать участникам проекта."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #555555; font-size: 13px;")
        card.layout.addWidget(subtitle)

        # Название роли
        name_label = FieldLabel("Название роли")
        card.layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("InputField")
        self.name_input.setPlaceholderText("Например: Разработчик, Аналитик, Тимлид")
        self.name_input.setFixedHeight(44)
        card.layout.addWidget(self.name_input)

        # Ставка (опционально)
        rate_label = FieldLabel("Ставка (0–10, необязательно)")
        card.layout.addWidget(rate_label)

        self.rate_input = QSpinBox()
        # Используем -1 как «нет значения»
        self.rate_input.setRange(-1, 10)
        self.rate_input.setValue(-1)
        self.rate_input.setSpecialValueText("—")
        self.rate_input.setObjectName("SpinBox")
        self.rate_input.setFixedHeight(44)
        card.layout.addWidget(self.rate_input)

        # Кнопки
        buttons_row = QHBoxLayout()
        buttons_row.setContentsMargins(0, 0, 0, 0)
        buttons_row.setSpacing(12)

        create_btn = PrimaryButton("Создать")
        create_btn.setFixedHeight(40)
        create_btn.clicked.connect(self._on_create_clicked)
        buttons_row.addWidget(create_btn)

        buttons_row.addStretch()

        cancel_btn = SecondaryButton("Отмена")
        cancel_btn.setFixedHeight(40)
        cancel_btn.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_btn)

        card.layout.addLayout(buttons_row)

        root_layout.addWidget(card)

    # ----- Actions -----

    def _on_create_clicked(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка валидации", "Название роли обязательно.")
            return

        rate_value = self.rate_input.value()
        rate = None if rate_value < 0 else rate_value

        data = ProjectRoleCreateDTO(RoleName=name, Rate=rate)

        try:
            role = projects_api.create_project_role(
                self.project_id,
                data,
                self.auth_service.token,
            )
            self.role_created.emit(role)
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось создать роль:\n{e}",
            )

