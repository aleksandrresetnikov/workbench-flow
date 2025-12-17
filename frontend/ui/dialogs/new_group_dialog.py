from typing import Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QMessageBox, QWidget

from api.dtos import ProjectDTO, TaskGroupCreateDTO, TaskGroupDTO
from api.task_groups import task_groups_api
from services.auth_service import AuthService
from ui.components import ModalCard, FieldLabel, PrimaryButton


class NewTaskGroupDialog(QDialog):
    """Диалог создания новой группы задач (колонки)."""

    group_created = Signal(TaskGroupDTO)

    def __init__(self, project: ProjectDTO, auth_service: AuthService, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project = project
        self.auth_service = auth_service

        self.setWindowTitle("Новая группа задач")
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(400)

        title = QLabel("Новая группа задач")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        card.layout.addWidget(title)

        card.layout.addWidget(FieldLabel("Наименование"))

        self.name_input = QLineEdit()
        self.name_input.setObjectName("InputField")
        self.name_input.setPlaceholderText("Например: В процессе")
        self.name_input.setFixedHeight(50)
        card.layout.addWidget(self.name_input)

        create_btn = PrimaryButton("Создать")
        create_btn.setFixedHeight(50)
        create_btn.clicked.connect(self._on_create_clicked)
        card.layout.addWidget(create_btn)

        layout.addWidget(card)

    def _on_create_clicked(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка валидации", "Наименование группы обязательно.")
            return

        data = TaskGroupCreateDTO(Name=name)

        try:
            token = self.auth_service.token
            if not token:
                raise RuntimeError("Отсутствует токен авторизации")
            group = task_groups_api.create_task_group(self.project.Id, data, token)
            self.group_created.emit(group)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать группу: {e}")


