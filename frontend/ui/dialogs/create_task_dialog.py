from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit,
    QHBoxLayout, QMessageBox, QComboBox, QDateEdit
)
from PySide6.QtCore import Qt, Signal, QDate
from datetime import date
from typing import Optional, List

from services.auth_service import AuthService
from api.tasks import tasks_api
from api.dtos import TaskCreateDTO, TaskDTO, TaskGroupDTO
from api.dtos import ProjectMemberWithUserDTO
from ui.components import ModalCard, PrimaryButton, SecondaryButton


FIELD_HEIGHT = 40
LABEL_STYLE = """
QLabel {
    font-size: 13px;
    color: #1F2937;
    margin: 0;
    padding: 0;
}
"""


class CreateTaskDialog(QDialog):
    task_created = Signal(TaskDTO)

    def __init__(
        self,
        auth_service: AuthService,
        project_id: int,
        members: list[ProjectMemberWithUserDTO],
        groups: Optional[List[TaskGroupDTO]] = None,
        preselected_group_id: Optional[int] = None,
        parent=None,
    ):
        super().__init__(parent)

        self.auth_service = auth_service
        self.project_id = project_id
        self.members = members or []
        self.groups = groups or []

        self.setWindowTitle("Новая задача")
        self.setModal(True)
        self.setFixedSize(640, 560)

        self._setup_ui(preselected_group_id)

    # ---------- helpers ----------
    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(LABEL_STYLE)
        return lbl

    def _setup_ui(self, preselected_group_id):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(0, 0, 0, 0)

        card = ModalCard()
        card.setFixedWidth(600)
        card.layout.setSpacing(16)
        card.layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("Новая задача")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        card.layout.addWidget(title)

        # --- Name ---
        card.layout.addWidget(self._label("Наименование"))
        self.name_input = QLineEdit()
        self.name_input.setFixedHeight(FIELD_HEIGHT)
        card.layout.addWidget(self.name_input)

        # --- Description ---
        card.layout.addWidget(self._label("Описание"))
        self.desc_input = QTextEdit()
        self.desc_input.setFixedHeight(FIELD_HEIGHT)
        self.desc_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #C9CDD4;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        card.layout.addWidget(self.desc_input)

        # --- Group ---
        card.layout.addWidget(self._label("Группа задачи (обязательно)"))
        self.group_combo = QComboBox()
        self.group_combo.setFixedHeight(FIELD_HEIGHT)
        self.group_combo.addItem("Выберите группу", None)
        for g in self.groups:
            self.group_combo.addItem(g.Name, g.Id)

        if preselected_group_id:
            for i in range(self.group_combo.count()):
                if self.group_combo.itemData(i) == preselected_group_id:
                    self.group_combo.setCurrentIndex(i)
                    break

        card.layout.addWidget(self.group_combo)

        # --- Deadline ---
        card.layout.addWidget(self._label("Сроки выполнения"))
        self.deadline_input = QDateEdit()
        self.deadline_input.setFixedHeight(FIELD_HEIGHT)
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate())
        card.layout.addWidget(self.deadline_input)

        # --- Responsible ---
        card.layout.addWidget(self._label("Ответственный (опционально)"))
        self.resp_combo = QComboBox()
        self.resp_combo.setFixedHeight(FIELD_HEIGHT)
        self.resp_combo.addItem("Не назначено", None)
        for m in self.members:
            u = m.member
            name = f"{u.FirstName or ''} {u.LastName or ''}".strip() or u.Username
            self.resp_combo.addItem(f"{name} — {u.Email}", u.Id)
        card.layout.addWidget(self.resp_combo)

        # --- Tags ---
        card.layout.addWidget(self._label("Теги (пока пусто)"))
        self.tags_input = QLineEdit()
        self.tags_input.setFixedHeight(FIELD_HEIGHT)
        self.tags_input.setPlaceholderText("Оставьте пустым")
        card.layout.addWidget(self.tags_input)

        # --- Buttons ---
        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        create_btn = PrimaryButton("Создать")
        create_btn.clicked.connect(self._on_create_clicked)

        cancel_btn = SecondaryButton("Отмена")
        cancel_btn.clicked.connect(self.reject)

        buttons.addWidget(create_btn)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)

        card.layout.addLayout(buttons)
        root.addWidget(card)

    # ---------- actions ----------
    def _on_create_clicked(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите наименование задачи")
            return

        if self.group_combo.currentData() is None:
            QMessageBox.warning(self, "Ошибка", "Выберите группу задачи")
            return

        qdate = self.deadline_input.date()
        deadline = date(qdate.year(), qdate.month(), qdate.day())

        data = TaskCreateDTO(
            Title=self.name_input.text().strip(),
            # Backend requires Text to be a string (not null) — send empty string when description is empty
            Text=self.desc_input.toPlainText().strip() or "",
            DeadLine=deadline,
            TargetId=self.resp_combo.currentData(),
            GroupId=self.group_combo.currentData(),
        )

        try:
            task = tasks_api.create_task(
                self.project_id, data, self.auth_service.token
            )
            self.task_created.emit(task)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
