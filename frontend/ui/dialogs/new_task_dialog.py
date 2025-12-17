from typing import List, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QDateEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QWidget,
)

from api.dtos import ProjectDTO, TaskCreateDTO, TaskDTO, ProjectMemberWithUserDTO
from api.tasks import tasks_api
from services.auth_service import AuthService
from ui.components import ModalCard, FieldLabel, PrimaryButton


class NewTaskDialog(QDialog):
    """Диалог создания новой задачи."""

    task_created = Signal(TaskDTO)

    def __init__(
        self,
        project: ProjectDTO,
        auth_service: AuthService,
        members: List[ProjectMemberWithUserDTO],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.project = project
        self.auth_service = auth_service
        self.members = members
        self._selected_member: Optional[ProjectMemberWithUserDTO] = None

        self.setWindowTitle("Новая задача")
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(550)

        title = QLabel("Новая задача")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        card.layout.addWidget(title)

        # Name
        card.layout.addWidget(FieldLabel("Наименование"))
        self.name_input = QLineEdit()
        self.name_input.setObjectName("InputField")
        self.name_input.setPlaceholderText("Введите наименование задачи")
        self.name_input.setFixedHeight(50)
        card.layout.addWidget(self.name_input)

        # Description
        card.layout.addWidget(FieldLabel("Описание"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText("Введите описание задачи")
        self.desc_input.setMaximumHeight(120)
        card.layout.addWidget(self.desc_input)

        # Deadline
        card.layout.addWidget(FieldLabel("Сроки выполнения"))
        self.deadline_input = QDateEdit()
        self.deadline_input.setObjectName("DateEdit")
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setFixedHeight(50)
        card.layout.addWidget(self.deadline_input)

        # Tags (пока простая строка)
        card.layout.addWidget(FieldLabel("Теги"))
        self.tags_input = QLineEdit()
        self.tags_input.setObjectName("InputField")
        self.tags_input.setPlaceholderText("Например: Дизайн, Баг")
        self.tags_input.setFixedHeight(50)
        card.layout.addWidget(self.tags_input)

        # Assignee search
        card.layout.addWidget(FieldLabel("Ответственный (поиск по email/username)"))
        self.assignee_input = QLineEdit()
        self.assignee_input.setObjectName("InputField")
        self.assignee_input.setPlaceholderText("Введите email или username")
        self.assignee_input.textChanged.connect(self._update_suggestions)
        card.layout.addWidget(self.assignee_input)

        self.suggestions = QListWidget()
        self.suggestions.setObjectName("AssigneeSuggestions")
        self.suggestions.itemClicked.connect(self._on_suggestion_clicked)
        self.suggestions.setVisible(False)
        card.layout.addWidget(self.suggestions)

        # Create button
        create_btn = PrimaryButton("Создать")
        create_btn.setFixedHeight(50)
        create_btn.clicked.connect(self._on_create_clicked)
        card.layout.addWidget(create_btn)

        layout.addWidget(card)

    # ---------- Assignee search ----------
    def _update_suggestions(self, text: str) -> None:
        self.suggestions.clear()
        text = text.strip().lower()
        if not text:
            self.suggestions.setVisible(False)
            self._selected_member = None
            return

        for member in self.members:
            user = member.member
            haystack = f"{user.Username} {user.Email}".lower()
            if text in haystack:
                item = QListWidgetItem(f"{user.Username} ({user.Email})")
                item.setData(Qt.UserRole, member)
                self.suggestions.addItem(item)

        self.suggestions.setVisible(self.suggestions.count() > 0)

    def _on_suggestion_clicked(self, item: QListWidgetItem) -> None:
        member = item.data(Qt.UserRole)
        self._selected_member = member
        user = member.member
        self.assignee_input.setText(user.Email)
        self.suggestions.setVisible(False)

    # ---------- Create ----------
    def _on_create_clicked(self) -> None:
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка валидации", "Наименование задачи обязательно.")
            return

        desc = self.desc_input.toPlainText().strip() or None

        # Пока API задач не поддерживает deadline/tags/assignee, сохраняем только базовые поля.
        task_data = TaskCreateDTO(Name=name, Description=desc, GroupId=None, Status="New")

        try:
            token = self.auth_service.token
            if not token:
                raise RuntimeError("Отсутствует токен авторизации")
            task = tasks_api.create_task(self.project.Id, task_data, token)
            self.task_created.emit(task)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {e}")


