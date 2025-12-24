from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QScrollArea
)
from PySide6.QtCore import Qt

from api.dtos import TaskGroupDTO, TaskDTO
from ui.components.kanban_column import KanbanColumn


class KanbanBoard(QWidget):
    def __init__(
        self,
        groups: list[TaskGroupDTO],
        tasks: list[TaskDTO],
        parent=None
    ):
        super().__init__(parent)
        self.groups = groups
        self.tasks = tasks

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("border: none;")

        self.content = QWidget()
        self.content_layout = QHBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)

        self._populate_board()

        self.content_layout.addStretch()
        scroll.setWidget(self.content)

        layout.addWidget(scroll)

    def _populate_board(self):
        for group in self.groups:
            group_tasks = [
                t for t in self.tasks if t.GroupId == group.Id
            ]
            self.content_layout.addWidget(
                KanbanColumn(group, group_tasks)
            )

    def update_board(self, groups: list[TaskGroupDTO], tasks: list[TaskDTO]):
        self.groups = groups
        self.tasks = tasks

        # Clear existing
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._populate_board()
        self.content_layout.addStretch()
