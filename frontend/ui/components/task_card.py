from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from api.dtos import TaskDTO


class TaskCard(QWidget):
    """
    Компонент карточки задачи для канбан-доски.
    """

    def __init__(self, task: TaskDTO, parent=None):
        super().__init__(parent)
        self.task = task
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("TaskCard")
        self.setStyleSheet("""
            QWidget#TaskCard {
                background-color: #FFFFFF;
                border: 1px solid #E1E5E9;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
            }
            QWidget#TaskCard:hover {
                border-color: #007BFF;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Название задачи
        title_label = QLabel(self.task.Name)
        title_label.setObjectName("TaskTitle")
        title_label.setStyleSheet("""
            QLabel#TaskTitle {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        layout.addWidget(title_label)

        # Описание задачи (если есть)
        if self.task.Description:
            desc_label = QLabel(self.task.Description)
            desc_label.setObjectName("TaskDescription")
            desc_label.setStyleSheet("""
                QLabel#TaskDescription {
                    font-size: 12px;
                    color: #666666;
                    word-wrap: true;
                }
            """)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # Теги (используем Status как тег)
        if self.task.Status:
            tags_layout = QHBoxLayout()
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(4)

            # Разделим Status по запятой, если несколько
            tags = [tag.strip() for tag in self.task.Status.split(',')]
            for tag in tags:
                tag_label = QLabel(tag)
                tag_label.setObjectName("TaskTag")
                tag_label.setStyleSheet("""
                    QLabel#TaskTag {
                        background-color: #E3F2FD;
                        color: #1976D2;
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-size: 10px;
                        font-weight: bold;
                    }
                """)
                tags_layout.addWidget(tag_label)

            tags_layout.addStretch()
            layout.addLayout(tags_layout)

        # Дата создания (опционально, внизу)
        created_label = QLabel(f"Создано: {self.task.CreatedAt.strftime('%d.%m.%Y')}")
        created_label.setObjectName("TaskCreated")
        created_label.setStyleSheet("""
            QLabel#TaskCreated {
                font-size: 10px;
                color: #999999;
            }
        """)
        layout.addWidget(created_label)