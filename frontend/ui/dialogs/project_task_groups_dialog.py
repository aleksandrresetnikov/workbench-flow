from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush
from datetime import datetime

from services.auth_service import AuthService
from api.task_groups import task_groups_api
from api.dtos import TaskGroupDTO
from ui.components import ModalCard, PrimaryButton, SecondaryButton
from ui.dialogs.create_task_group_dialog import CreateTaskGroupDialog


class ProjectTaskGroupsDialog(QDialog):
    """Диалог управления группами задач проекта: список + создание/удаление."""

    def __init__(self, auth_service: AuthService, project_id: int, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.project_id = project_id
        self.groups: list[TaskGroupDTO] = []

        self.setWindowTitle("Группы задач проекта")
        self.setModal(True)
        self.setFixedSize(720, 420)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()
        self._load_groups()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setAlignment(Qt.AlignCenter)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(680)

        title = QLabel("Группы задач")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet(
            "color: #000000; font-size: 22px; font-weight: bold; margin-bottom: 12px;"
        )
        card.layout.addWidget(title)

        subtitle = QLabel(
            "Просматривайте и управляйте колонками (группами задач) для этого проекта."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #555555; font-size: 13px;")
        card.layout.addWidget(subtitle)

        # Таблица групп
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Название группы", "Создана"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(False)
        self.table.setFixedHeight(300)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #13243A;
                color: #FFFFFF;
                border: none;
            }
            QTableWidget::item {
                background-color: transparent;
                padding: 8px;
                border: none;
            }
            QHeaderView::section {
                background-color: #D1E9FF;
                color: #000000;
                padding: 10px;
                border: none;
            }
        """)
        card.layout.addWidget(self.table)

        # Кнопки
        buttons_row = QHBoxLayout()
        buttons_row.setContentsMargins(0, 0, 0, 0)
        buttons_row.setSpacing(12)

        add_group_btn = PrimaryButton("Добавить группу")
        add_group_btn.setFixedHeight(40)
        add_group_btn.clicked.connect(self._open_create_group_dialog)
        buttons_row.addWidget(add_group_btn)

        remove_btn = SecondaryButton("Удалить группу")
        remove_btn.setFixedHeight(40)
        remove_btn.clicked.connect(self._remove_selected_group)
        buttons_row.addWidget(remove_btn)

        buttons_row.addStretch()

        close_btn = SecondaryButton("Закрыть")
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(self.reject)
        buttons_row.addWidget(close_btn)

        card.layout.addLayout(buttons_row)

        root_layout.addWidget(card)

    def _load_groups(self):
        try:
            self.groups = task_groups_api.get_task_groups_for_project(
                self.project_id, self.auth_service.token
            )
            self._populate_table()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить группы задач:\n{e}",
            )

    def _populate_table(self):
        self.table.setRowCount(len(self.groups))

        for row, group in enumerate(self.groups):
            name_item = QTableWidgetItem(group.Name)
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            name_item.setForeground(QBrush(QColor("#FFFFFF")))
            self.table.setItem(row, 0, name_item)

            created_at = group.CreateDate
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at)
                except ValueError:
                    pass

            if isinstance(created_at, datetime):
                created_text = created_at.strftime("%d.%m.%Y %H:%M")
            else:
                created_text = str(created_at)

            created_item = QTableWidgetItem(created_text)
            created_item.setFlags(created_item.flags() ^ Qt.ItemIsEditable)
            created_item.setForeground(QBrush(QColor("#FFFFFF")))
            self.table.setItem(row, 1, created_item)

        self.table.resizeColumnsToContents()

    def _open_create_group_dialog(self):
        dialog = CreateTaskGroupDialog(self.auth_service, self.project_id, parent=self)

        def on_group_created(group: TaskGroupDTO):
            # Добавим в список и перерисуем
            self.groups.append(group)
            self._populate_table()

        dialog.group_created.connect(on_group_created)
        dialog.exec()

    def _get_selected_group(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self.groups):
            return None
        return self.groups[row]

    def _remove_selected_group(self):
        group = self._get_selected_group()
        if not group:
            QMessageBox.warning(self, "Не выбрана группа", "Выберите группу, которую нужно удалить.")
            return

        confirm = QMessageBox.question(
            self,
            "Удалить группу",
            f"Вы действительно хотите удалить группу\n\"{group.Name}\"?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            task_groups_api.delete_task_group(group.Id, self.auth_service.token)
            self._load_groups()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить группу:\n{e}")