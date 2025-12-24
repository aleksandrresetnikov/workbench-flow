from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from api.dtos import TaskGroupDTO, TaskDTO
from ui.components.task_card import TaskCard


class KanbanColumn(QWidget):
    def __init__(
        self,
        group: TaskGroupDTO,
        tasks: list[TaskDTO],
        parent=None
    ):
        super().__init__(parent)
        self.group = group
        self.tasks = tasks

        self._setup_ui()

    def _setup_ui(self):
        self.setFixedWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # ---- Header ----
        title = QLabel(f"{self.group.Name} ({len(self.tasks)})")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #13243A;")
        layout.addWidget(title)

        # ---- Scroll with tasks ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none;")

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        for task in self.tasks:
            content_layout.addWidget(TaskCard(task))

        content_layout.addStretch()
        scroll.setWidget(content)

        layout.addWidget(scroll)
