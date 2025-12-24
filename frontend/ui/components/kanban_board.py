from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from api.dtos import TaskGroupDTO, TaskDTO
from .task_card import TaskCard


class KanbanBoard(QWidget):
    """
    Компонент канбан-доски с колонками как task groups и задачами как карточками.
    """

    def __init__(self, task_groups: list[TaskGroupDTO], tasks: list[TaskDTO], parent=None):
        super().__init__(parent)
        self.task_groups = task_groups
        self.tasks = tasks
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area для колонок
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #FFFFFF;
            }
        """)

        # Контейнер для колонок
        columns_widget = QWidget()
        columns_widget.setStyleSheet("background-color: #FFFFFF;")
        columns_layout = QHBoxLayout(columns_widget)
        columns_layout.setContentsMargins(0, 16, 0, 16)
        columns_layout.setSpacing(16)

        # Создаем колонки для каждой task group
        for group in self.task_groups:
            column = self._create_column(group)
            columns_layout.addWidget(column)

        scroll_area.setWidget(columns_widget)
        layout.addWidget(scroll_area)

    def _create_column(self, group: TaskGroupDTO) -> QWidget:
        """Создает колонку для task group."""
        column = QWidget()
        column.setObjectName("KanbanColumn")
        column.setStyleSheet("""
            QWidget#KanbanColumn {
                background-color: #F8F9FA;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
                min-width: 280px;
                max-width: 280px;
            }
        """)

        layout = QVBoxLayout(column)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Название группы
        group_label = QLabel(group.Name)
        group_label.setObjectName("GroupLabel")
        group_label.setStyleSheet("""
            QLabel#GroupLabel {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                padding-bottom: 8px;
            }
        """)
        layout.addWidget(group_label)

        # Задачи в этой группе
        group_tasks = [task for task in self.tasks if task.GroupId == group.Id]
        if group_tasks:
            for task in group_tasks:
                task_card = TaskCard(task)
                layout.addWidget(task_card)
        else:
            # Заглушка, если нет задач
            empty_label = QLabel("Нет задач")
            empty_label.setObjectName("EmptyLabel")
            empty_label.setStyleSheet("""
                QLabel#EmptyLabel {
                    color: #999999;
                    font-style: italic;
                    padding: 20px;
                }
            """)
            empty_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(empty_label)

        layout.addStretch()  # Чтобы задачи были сверху

        return column