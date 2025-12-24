from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from services.auth_service import AuthService
from api.task_groups import task_groups_api
from api.dtos import TaskGroupCreateDTO, TaskGroupDTO
from ui.components import ModalCard, FieldLabel, PrimaryButton, SecondaryButton


class CreateTaskGroupDialog(QDialog):
    """Вложенный диалог для создания группы задач в проекте."""

    group_created = Signal(TaskGroupDTO)

    def __init__(self, auth_service: AuthService, project_id: int, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.project_id = project_id

        self.setWindowTitle("Новая группа задач")
        self.setModal(True)
        self.setFixedSize(520, 200)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setAlignment(Qt.AlignCenter)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(480)

        title = QLabel("Новая группа")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet(
            "color: #000000; font-size: 20px; font-weight: bold; margin-bottom: 12px;"
        )
        card.layout.addWidget(title)

        subtitle = QLabel("Создайте колонку (группу задач) для канбан-доски проекта.")
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #555555; font-size: 13px;")
        card.layout.addWidget(subtitle)

        name_label = FieldLabel("Название группы")
        card.layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("InputField")
        self.name_input.setPlaceholderText("Например: Backlog, В работе, Готово")
        self.name_input.setFixedHeight(44)
        card.layout.addWidget(self.name_input)

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

    def _on_create_clicked(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка валидации", "Название группы обязательно.")
            return

        data = TaskGroupCreateDTO(Name=name)

        try:
            group = task_groups_api.create_task_group(
                self.project_id,
                data,
                self.auth_service.token,
            )
            self.group_created.emit(group)
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось создать группу:{e}",
            )