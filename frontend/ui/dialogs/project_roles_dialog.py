from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Qt
from datetime import datetime

from services.auth_service import AuthService
from api.projects import projects_api
from api.dtos import ProjectRoleDTO
from ui.components import ModalCard, PrimaryButton, SecondaryButton
from ui.dialogs.create_project_role_dialog import CreateProjectRoleDialog


class ProjectRolesDialog(QDialog):
    """Диалог управления ролями проекта: таблица ролей + кнопка добавления роли."""

    def __init__(self, auth_service: AuthService, project_id: int, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.project_id = project_id
        self.roles: list[ProjectRoleDTO] = []

        self.setWindowTitle("Роли участников проекта")
        self.setModal(True)
        # Фиксированный размер и полупрозрачный фон
        self.setFixedSize(720, 420)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()
        self._load_roles()

    # ----- UI -----

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setAlignment(Qt.AlignCenter)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(650)

        # Заголовок
        title = QLabel("Роли участников проекта")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet(
            "color: #000000; font-size: 22px; font-weight: bold; margin-bottom: 12px;"
        )
        card.layout.addWidget(title)

        subtitle = QLabel(
            "Управляйте пользовательскими ролями внутри проекта. "
            "Роли можно привязывать к участникам при настройке доступа."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #555555; font-size: 13px;")
        card.layout.addWidget(subtitle)

        # Таблица ролей (без поля Rate)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Название роли", "Создана"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(220)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setFixedHeight(260)
        card.layout.addWidget(self.table)

        # Кнопки
        buttons_row = QHBoxLayout()
        buttons_row.setContentsMargins(0, 0, 0, 0)
        buttons_row.setSpacing(12)

        add_role_btn = PrimaryButton("Добавить роль")
        add_role_btn.setFixedHeight(40)
        add_role_btn.clicked.connect(self._open_create_role_dialog)
        buttons_row.addWidget(add_role_btn)

        buttons_row.addStretch()

        close_btn = SecondaryButton("Закрыть")
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(self.reject)
        buttons_row.addWidget(close_btn)

        card.layout.addLayout(buttons_row)

        root_layout.addWidget(card)

    # ----- Data -----

    def _load_roles(self):
        """Загрузить роли проекта и отобразить их в таблице."""
        try:
            self.roles = projects_api.get_project_roles(
                self.project_id, self.auth_service.token
            )
            self._populate_table()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить роли проекта:\n{e}",
            )

    def _populate_table(self):
        self.table.setRowCount(len(self.roles))

        for row, role in enumerate(self.roles):
            # Название роли
            name_item = QTableWidgetItem(role.RoleName)
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row, 0, name_item)

            # Дата создания (читаемый формат)
            created_at = role.CreateDate
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
            self.table.setItem(row, 1, created_item)

        self.table.resizeColumnsToContents()

    # ----- Actions -----

    def _open_create_role_dialog(self):
        """Открыть вложенный диалог создания роли и обновить таблицу после успеха."""
        dialog = CreateProjectRoleDialog(
            auth_service=self.auth_service,
            project_id=self.project_id,
            parent=self,
        )

        def on_role_created(_role: ProjectRoleDTO):
            # Добавим в локальный список и перерисуем таблицу
            self.roles.append(_role)
            self._populate_table()

        dialog.role_created.connect(on_role_created)
        dialog.exec()