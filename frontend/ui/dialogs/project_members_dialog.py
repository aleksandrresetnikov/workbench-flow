from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QLineEdit,
    QTableWidgetSelectionRange,
    QComboBox,
    QCheckBox,
)
from typing import Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush

from services.auth_service import AuthService
from api.projects import projects_api
from api.users import users_api
from api.dtos import (
    ProjectMemberWithUserDTO,
    ProjectRoleDTO,
    ProjectMemberCreateDTO,
    UserDTO,
)
from ui.components import ModalCard, PrimaryButton, SecondaryButton, FieldLabel


def _translate_access_level(access_level: str, is_owner: bool = False) -> str:
    if is_owner:
        return "Владелец"
    mapping = {
        "Admin": "Администратор",
        "Common": "Участник",
        "admin": "Администратор",
        "common": "Участник",
    }
    return mapping.get(access_level, access_level)


class AddProjectMemberDialog(QDialog):
    """Вложенный диалог для добавления участника проекта."""

    member_added = Signal()

    def __init__(
        self,
        auth_service: AuthService,
        project_id: int,
        roles: list[ProjectRoleDTO],
        existing_member_ids: set[int],
        parent=None,
    ):
        super().__init__(parent)
        self.auth_service = auth_service
        self.project_id = project_id
        self.roles = roles
        self.existing_member_ids = existing_member_ids

        self.all_users: list[UserDTO] = []
        self.filtered_users: list[UserDTO] = []

        self.setWindowTitle("Добавить участника проекта")
        self.setModal(True)
        self.setFixedSize(720, 420)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()
        self._load_users()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setAlignment(Qt.AlignCenter)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(680)

        title = QLabel("Добавить участника")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet(
            "color: #000000; font-size: 20px; font-weight: bold; margin-bottom: 8px;"
        )
        card.layout.addWidget(title)

        subtitle = QLabel(
            "Найдите пользователя по email или имени и укажите его права доступа в этом проекте."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #555555; font-size: 13px;")
        card.layout.addWidget(subtitle)

        # Поиск пользователя
        search_label = FieldLabel("Поиск пользователя (email или имя)")
        card.layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("InputField")
        self.search_input.setPlaceholderText("Начните вводить email или имя пользователя")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self._apply_filter)
        card.layout.addWidget(self.search_input)

        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(2)
        self.users_table.setHorizontalHeaderLabels(["Пользователь", "Email"])
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SingleSelection)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.verticalHeader().setVisible(False)
        # Disable Qt alternating row default (we handle visuals via stylesheet)
        self.users_table.setAlternatingRowColors(False)
        self.users_table.setFixedHeight(200)
        # Apply consistent modal table styling: dark background, light header
        self.users_table.setStyleSheet("""
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
            QTableWidget::item:selected {
                background-color: #1F3550;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #D1E9FF;
                color: #000000;
                padding: 10px;
                border: none;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #D1E9FF;
                border: none;
            }
        """)
        card.layout.addWidget(self.users_table)

        # Настройки доступа
        self.admin_checkbox = QCheckBox("Сделать администратором проекта")
        self.admin_checkbox.setChecked(False)
        card.layout.addWidget(self.admin_checkbox)

        role_label = FieldLabel("Роль в проекте (необязательно)")
        card.layout.addWidget(role_label)

        self.role_combo = QComboBox()
        self.role_combo.setObjectName("ComboBox")
        self.role_combo.setFixedHeight(40)
        self.role_combo.addItem("Без роли", userData=None)
        for role in self.roles:
            self.role_combo.addItem(role.RoleName, userData=role.Id)
        card.layout.addWidget(self.role_combo)

        # Кнопки
        buttons_row = QHBoxLayout()
        buttons_row.setContentsMargins(0, 0, 0, 0)
        buttons_row.setSpacing(12)

        add_btn = PrimaryButton("Добавить")
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self._on_add_clicked)
        buttons_row.addWidget(add_btn)

        buttons_row.addStretch()

        cancel_btn = SecondaryButton("Отмена")
        cancel_btn.setFixedHeight(40)
        cancel_btn.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_btn)

        card.layout.addLayout(buttons_row)

        root_layout.addWidget(card)

    def _load_users(self):
        """Загрузить всех пользователей и отфильтровать тех, кто уже в проекте."""
        try:
            users = users_api.get_users(self.auth_service.token)
            # Исключаем уже добавленных участников
            self.all_users = [u for u in users if u.Id not in self.existing_member_ids]
            self._apply_filter(self.search_input.text())
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить список пользователей:\n{e}",
            )

    def _apply_filter(self, text: str):
        query = (text or "").strip().lower()
        if not query:
            self.filtered_users = list(self.all_users)
        else:
            self.filtered_users = [
                u
                for u in self.all_users
                if query in (u.Email or "").lower()
                or query in (u.Username or "").lower()
            ]

        self._populate_users_table()

    def _populate_users_table(self):
        self.users_table.setRowCount(len(self.filtered_users))
        for row, user in enumerate(self.filtered_users):
            name_parts = [
                user.FirstName or "",
                user.LastName or "",
            ]
            full_name = " ".join(p for p in name_parts if p).strip() or user.Username

            name_item = QTableWidgetItem(full_name)
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            name_item.setForeground(QBrush(QColor("#FFFFFF")))
            self.users_table.setItem(row, 0, name_item)

            email_item = QTableWidgetItem(user.Email)
            email_item.setFlags(email_item.flags() ^ Qt.ItemIsEditable)
            email_item.setForeground(QBrush(QColor("#FFFFFF")))
            self.users_table.setItem(row, 1, email_item)

        self.users_table.resizeColumnsToContents()

    def _get_selected_user(self) -> Optional[UserDTO]:
        row = self.users_table.currentRow()
        if row < 0 or row >= len(self.filtered_users):
            return None
        return self.filtered_users[row]

    def _on_add_clicked(self):
        user = self._get_selected_user()
        if not user:
            QMessageBox.warning(self, "Не выбран пользователь", "Выберите пользователя из списка.")
            return

        access_level = "Admin" if self.admin_checkbox.isChecked() else None
        role_id = self.role_combo.currentData()

        member_data = ProjectMemberCreateDTO(
            MemnerId=user.Id,
            RoleId=role_id,
        )

        try:
            created = projects_api.add_project_member(
                self.project_id,
                member_data,
                self.auth_service.token,
            )

            # Если прозапрошен админ-бокс — сразу обновляем уровень доступа через отдельный вызов
            if access_level == "Admin":
                try:
                    projects_api.update_project_member_access(
                        self.project_id,
                        created.Id,
                        ProjectMemberBaseDTO(AccessLevel="Admin"),
                        self.auth_service.token,
                    )
                except Exception as inner_e:
                    # логируем, но не блокируем добавление
                    QMessageBox.warning(self, "Внимание", f"Участник добавлен, но не удалось назначить администратора:\n{inner_e}")

            self.member_added.emit()
            self.accept()
        except Exception as e:
            # Показать подробный ответ от API, если он есть (часто содержит валидационные ошибки)
            detail = str(e)
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось добавить участника:\n{detail}",
            )


class ConfirmRemoveMemberDialog(QDialog):
    """Подтверждение удаления участника проекта."""

    def __init__(self, member_name: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Удалить участника")
        self.setModal(True)
        self.setFixedSize(420, 180)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        card = ModalCard()

        label = QLabel(
            f"Вы действительно хотите удалить участника\n<b>{member_name}</b>\nиз проекта?"
        )
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        card.layout.addWidget(label)

        buttons_row = QHBoxLayout()
        buttons_row.setContentsMargins(0, 0, 0, 0)
        buttons_row.setSpacing(12)

        confirm_btn = PrimaryButton("Удалить")
        confirm_btn.setFixedHeight(36)
        confirm_btn.clicked.connect(self.accept)
        buttons_row.addWidget(confirm_btn)

        buttons_row.addStretch()

        cancel_btn = SecondaryButton("Отмена")
        cancel_btn.setFixedHeight(36)
        cancel_btn.clicked.connect(self.reject)
        buttons_row.addWidget(cancel_btn)

        card.layout.addLayout(buttons_row)

        layout.addWidget(card)


class ProjectMembersDialog(QDialog):
    """Диалог управления участниками проекта: список + добавление/удаление."""

    def __init__(self, auth_service: AuthService, project_id: int, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.project_id = project_id

        self.members: list[ProjectMemberWithUserDTO] = []
        self.roles: list[ProjectRoleDTO] = []

        self.setWindowTitle("Участники проекта")
        self.setModal(True)
        self.setFixedSize(820, 480)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setAlignment(Qt.AlignCenter)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(780)

        title = QLabel("Участники проекта")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet(
            "color: #000000; font-size: 22px; font-weight: bold; margin-bottom: 12px;"
        )
        card.layout.addWidget(title)

        subtitle = QLabel(
            "Просматривайте участников проекта, назначайте администраторов и роли, добавляйте и удаляйте участников."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #555555; font-size: 13px;")
        card.layout.addWidget(subtitle)

        # Таблица участников
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Пользователь", "Email", "Доступ", "Роль в проекте"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        # Disable default alternating rows (we style rows consistently)
        self.table.setAlternatingRowColors(False)
        self.table.setFixedHeight(300)
        # Apply consistent modal table styling: dark background, light header
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
            QTableWidget::item:selected {
                background-color: #1F3550;
                color: #FFFFFF;
            }
            QHeaderView::section {
                background-color: #D1E9FF;
                color: #000000;
                padding: 10px;
                border: none;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #D1E9FF;
                border: none;
            }
        """)
        card.layout.addWidget(self.table)

        # Кнопки управления
        buttons_row = QHBoxLayout()
        buttons_row.setContentsMargins(0, 0, 0, 0)
        buttons_row.setSpacing(12)

        add_btn = PrimaryButton("Добавить участника")
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self._open_add_member_dialog)
        buttons_row.addWidget(add_btn)

        remove_btn = SecondaryButton("Удалить участника")
        remove_btn.setFixedHeight(40)
        remove_btn.clicked.connect(self._remove_selected_member)
        buttons_row.addWidget(remove_btn)

        buttons_row.addStretch()

        close_btn = SecondaryButton("Закрыть")
        close_btn.setFixedHeight(40)
        close_btn.clicked.connect(self.reject)
        buttons_row.addWidget(close_btn)

        card.layout.addLayout(buttons_row)

        root_layout.addWidget(card)

    def _load_data(self):
        """Загрузить участников и роли проекта."""
        try:
            self.members = projects_api.get_project_members(
                self.project_id, self.auth_service.token
            )
            # Роли используются только для отображения названия и выбора в дочернем диалоге
            self.roles = projects_api.get_project_roles(
                self.project_id, self.auth_service.token
            )
            self._populate_table()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось загрузить участников проекта:\n{e}",
            )

    def _populate_table(self):
        self.table.setRowCount(len(self.members))

        roles_by_id = {r.Id: r.RoleName for r in self.roles}

        for row, member in enumerate(self.members):
            user = member.member
            name_parts = [
                user.FirstName or "",
                user.LastName or "",
            ]
            full_name = " ".join(p for p in name_parts if p).strip() or user.Username

            is_owner = False  # В этом диалоге нет информации о владельце, поэтому оставим False
            access_label = _translate_access_level(member.AccessLevel, is_owner=is_owner)

            role_name = roles_by_id.get(getattr(member, "RoleId", None), "—")

            name_item = QTableWidgetItem(full_name)
            name_item.setFlags(name_item.flags() ^ Qt.ItemIsEditable)
            name_item.setForeground(QBrush(QColor("#FFFFFF")))
            self.table.setItem(row, 0, name_item)

            email_item = QTableWidgetItem(user.Email)
            email_item.setFlags(email_item.flags() ^ Qt.ItemIsEditable)
            email_item.setForeground(QBrush(QColor("#FFFFFF")))
            self.table.setItem(row, 1, email_item)

            access_item = QTableWidgetItem(access_label)
            access_item.setFlags(access_item.flags() ^ Qt.ItemIsEditable)
            access_item.setForeground(QBrush(QColor("#FFFFFF")))
            self.table.setItem(row, 2, access_item)

            role_item = QTableWidgetItem(role_name)
            role_item.setFlags(role_item.flags() ^ Qt.ItemIsEditable)
            role_item.setForeground(QBrush(QColor("#FFFFFF")))
            self.table.setItem(row, 3, role_item)

        self.table.resizeColumnsToContents()

    def _get_selected_member(self) -> Optional[ProjectMemberWithUserDTO]:
        row = self.table.currentRow()
        if row < 0 or row >= len(self.members):
            return None
        return self.members[row]

    def _open_add_member_dialog(self):
        existing_ids = {m.MemnerId for m in self.members}
        dialog = AddProjectMemberDialog(
            auth_service=self.auth_service,
            project_id=self.project_id,
            roles=self.roles,
            existing_member_ids=existing_ids,
            parent=self,
        )

        def on_member_added():
            self._load_data()

        dialog.member_added.connect(on_member_added)
        dialog.exec()

    def _remove_selected_member(self):
        member = self._get_selected_member()
        if not member:
            QMessageBox.warning(
                self,
                "Не выбран участник",
                "Выберите участника, которого нужно удалить.",
            )
            return

        user = member.member
        name_parts = [user.FirstName or "", user.LastName or ""]
        full_name = " ".join(p for p in name_parts if p).strip() or user.Username

        confirm_dialog = ConfirmRemoveMemberDialog(full_name, parent=self)
        if confirm_dialog.exec() != QDialog.Accepted:
            return

        try:
            projects_api.remove_project_member(
                self.project_id,
                member.Id,
                self.auth_service.token,
            )
            self._load_data()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось удалить участника:\n{e}",
            )