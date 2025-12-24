from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QHBoxLayout,
    QMessageBox,
    QComboBox,
    QDateEdit,
)
from PySide6.QtCore import Qt, Signal, QDate
from datetime import date
from typing import Optional, List

from services.auth_service import AuthService
from api.tasks import tasks_api
from api.dtos import TaskCreateDTO, TaskDTO, TaskGroupDTO
from api.dtos import ProjectMemberWithUserDTO
from ui.components import ModalCard, FieldLabel, PrimaryButton, SecondaryButton


class CreateTaskDialog(QDialog):
    """Диалог создания новой задачи в проекте."""

    task_created = Signal(TaskDTO)

    def __init__(self, auth_service: AuthService, project_id: int, members: list[ProjectMemberWithUserDTO], groups: Optional[List[TaskGroupDTO]] = None, preselected_group_id: Optional[int] = None, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.project_id = project_id
        self.members = members or []
        self.groups = groups or []
        self.preselected_group_id = preselected_group_id

        self.setWindowTitle("Новая задача")
        self.setModal(True)
        self.setFixedSize(640, 560)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setAlignment(Qt.AlignCenter)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(600)

        title = QLabel("Новая задача")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("color: #000000; font-size: 22px; font-weight: bold; margin-bottom: 12px;")
        card.layout.addWidget(title)

        # Name
        name_label = FieldLabel("Наименование")
        card.layout.addWidget(name_label)

        self.name_input = QLineEdit()
        self.name_input.setObjectName("InputField")
        self.name_input.setFixedHeight(44)
        card.layout.addWidget(self.name_input)

        # Description
        desc_label = FieldLabel("Описание")
        card.layout.addWidget(desc_label)

        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(120)
        card.layout.addWidget(self.desc_input)

        # Group (required)
        group_label = FieldLabel("Группа задачи (обязательно)")
        card.layout.addWidget(group_label)

        self.group_combo = QComboBox()
        self.group_combo.setObjectName("ComboBox")
        self.group_combo.setFixedHeight(40)
        # Add a placeholder to force explicit selection when no groups exist
        for g in self.groups:
            self.group_combo.addItem(g.Name, userData=g.Id)
        # Default selection: preselected_group_id or first group
        if self.preselected_group_id is not None:
            index = next((i for i, g in enumerate(self.groups) if g.Id == self.preselected_group_id), 0)
            self.group_combo.setCurrentIndex(index)
        elif self.groups:
            self.group_combo.setCurrentIndex(0)

        card.layout.addWidget(self.group_combo)

        # Deadline
        deadline_label = FieldLabel("Сроки выполнения")
        card.layout.addWidget(deadline_label)

        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDisplayFormat("dd.MM.yyyy")
        self.deadline_input.setDate(QDate.currentDate())
        self.deadline_input.setFixedHeight(36)
        card.layout.addWidget(self.deadline_input)

        # Responsible
        responsible_label = FieldLabel("Ответственный (опционально)")
        card.layout.addWidget(responsible_label)

        self.resp_combo = QComboBox()
        self.resp_combo.setObjectName("ComboBox")
        self.resp_combo.setFixedHeight(40)
        self.resp_combo.addItem("Не назначено", userData=None)
        for m in self.members:
            user = m.member
            full_name = f"{user.FirstName or ''} {user.LastName or ''}".strip() or user.Username
            display = f"{full_name} — {user.Email}"
            self.resp_combo.addItem(display, userData=user.Id)
        card.layout.addWidget(self.resp_combo)

        # Tags placeholder (empty)
        tags_label = FieldLabel("Теги (пока пусто)")
        card.layout.addWidget(tags_label)

        self.tags_input = QLineEdit()
        self.tags_input.setObjectName("InputField")
        self.tags_input.setPlaceholderText("Оставьте пустым")
        self.tags_input.setFixedHeight(36)
        card.layout.addWidget(self.tags_input)

        # Buttons
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
        title = self.name_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Ошибка валидации", "Наименование задачи обязательно.")
            return

        text = self.desc_input.toPlainText().strip() or None
        deadline_qdate = self.deadline_input.date()
        deadline_py = date(deadline_qdate.year(), deadline_qdate.month(), deadline_qdate.day()) if deadline_qdate.isValid() else None
        target = self.resp_combo.currentData()  # may be None
        group_id = self.group_combo.currentData()
        if group_id is None:
            QMessageBox.warning(self, "Ошибка валидации", "Пожалуйста, выберите группу задачи.")
            return

        data = TaskCreateDTO(
            Title=title,
            Text=text,
            DeadLine=deadline_py,
            TargetId=target,
            GroupId=group_id,
        )

        try:
            created = tasks_api.create_task(self.project_id, data, self.auth_service.token)
            self.task_created.emit(created)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу:\n{e}")