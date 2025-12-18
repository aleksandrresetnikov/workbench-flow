from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPixmap, QFont, QMouseEvent

from services.auth_service import AuthService
from api.projects import projects_api
from api.dtos import ProjectWithDetailsDTO, ProjectMemberWithUserDTO
from ui.components import UserDropdown, PrimaryButton, SecondaryButton
from ui.dialogs.project_members_dialog import ProjectMembersDialog
from ui.dialogs.project_roles_dialog import ProjectRolesDialog


class ProjectScreen(QWidget):
    """
    Экран отдельного проекта.

    Отображает шапку с навигацией «назад», информацией о проекте и пользователе,
    а также основную рабочую область, где позднее появится канбан-доска.
    """

    back_requested = Signal()
    logout_requested = Signal()

    def __init__(self, auth_service: AuthService, project_id: int, parent=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.project_id = project_id

        self.project: ProjectWithDetailsDTO | None = None
        self.members: list[ProjectMemberWithUserDTO] = []

        self._setup_ui()
        self._load_data()

    # ----- UI -----

    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.header = self._create_header()
        self.layout.addWidget(self.header)

        self.content = self._create_content_area()
        self.layout.addWidget(self.content)

    def _create_header(self) -> QWidget:
        header_widget = QWidget()
        header_widget.setObjectName("HeaderWidget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setSpacing(20)

        # Левая часть: кнопка "назад" и информация о проекте
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        back_row = QHBoxLayout()
        back_row.setContentsMargins(0, 0, 0, 0)
        back_row.setSpacing(16)

        back_btn = QPushButton("← К проектам")
        back_btn.setObjectName("BackButton")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedHeight(32)
        back_btn.setStyleSheet(
            """
            QPushButton#BackButton {
                background-color: #13243A;
                color: #FFFFFF;
                border-radius: 16px;
                padding: 6px 16px;
                font-size: 13px;
            }
            QPushButton#BackButton:hover {
                background-color: #1F3550;
            }
            """
        )
        back_btn.clicked.connect(self.back_requested.emit)
        back_row.addWidget(back_btn)

        # Название проекта
        self.project_name_label = QLabel("Название проекта")
        self.project_name_label.setObjectName("HeaderLabel")
        self.project_name_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #FFFFFF;"
        )
        back_row.addWidget(self.project_name_label)

        back_row.addStretch()

        left_layout.addLayout(back_row)

        # Дополнительная строка с метаданными проекта
        self.meta_label = QLabel("Задач: 0 • Участников: 0")
        self.meta_label.setObjectName("MetaLabel")
        self.meta_label.setStyleSheet("font-size: 12px; color: #FFFFFF;")
        # left_layout.addWidget(self.meta_label)

        header_layout.addWidget(left_container)

        header_layout.addStretch()

        # Правая часть: участники + кнопка добавить и пользователь
        right_container = QWidget()
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(16)

        # Участники (краткая подпись)
        self.participants_label = QLabel("Участники: 0")
        self.participants_label.setObjectName("ParticipantsLabel")
        self.participants_label.setStyleSheet("font-size: 13px; color: #FFFFFF;")
        right_layout.addWidget(self.meta_label)

        # Информация о текущем пользователе (как на главном экране)
        user_widget = QWidget()
        user_layout = QHBoxLayout(user_widget)
        user_layout.setSpacing(12)
        user_layout.setContentsMargins(0, 0, 0, 0)

        user_info = QWidget()
        user_info_layout = QVBoxLayout(user_info)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(2)

        name = f"{self.auth_service.current_user.FirstName or ''} {self.auth_service.current_user.LastName or ''}".strip()
        if not name:
            name = self.auth_service.current_user.Username

        name_label = QLabel(name)
        name_label.setObjectName("UserLabel")
        name_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        user_info_layout.addWidget(name_label)

        email_label = QLabel(self.auth_service.current_user.Email)
        email_label.setObjectName("UserLabel")
        email_label.setStyleSheet("font-size: 12px; color: #D1E9FF;")
        user_info_layout.addWidget(email_label)

        user_layout.addWidget(user_info)

        self.avatar_label = QLabel()
        self.avatar_label.setCursor(Qt.PointingHandCursor)
        try:
            pixmap = QPixmap("resources/profile_no_avatar.png")
            if not pixmap.isNull():
                pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.avatar_label.setPixmap(pixmap)
        except Exception:
            pass
        self.avatar_label.setFixedSize(40, 40)
        self.avatar_label.mousePressEvent = self._on_avatar_clicked  # type: ignore[assignment]
        user_layout.addWidget(self.avatar_label)

        right_layout.addWidget(user_widget)

        header_layout.addWidget(right_container)

        # Выпадающее меню пользователя
        self.dropdown = UserDropdown(self)
        self.dropdown.hide()
        self.dropdown.logout_requested.connect(self.logout_requested.emit)

        return header_widget

    def _create_content_area(self) -> QWidget:
        content = QFrame()
        content.setObjectName("ProjectContent")
        content.setStyleSheet("QFrame#ProjectContent { background-color: #FFFFFF; }")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(16)

        # Панель действий над задачами (горизонтальный бар под шапкой)
        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 0, 0, 0)
        actions_row.setSpacing(12)

        add_task_btn = PrimaryButton("Новая задача")
        add_task_btn.setFixedHeight(40)
        # Логику создания задачи добавим позже
        add_task_btn.setEnabled(False)
        actions_row.addWidget(add_task_btn)

        members_btn = SecondaryButton("Участники проекта")
        members_btn.setFixedHeight(40)
        members_btn.clicked.connect(self._open_members_dialog)
        actions_row.addWidget(members_btn)

        roles_btn = SecondaryButton("Роли участников")
        roles_btn.setFixedHeight(40)
        roles_btn.clicked.connect(self._open_roles_dialog)
        actions_row.addWidget(roles_btn)

        actions_row.addStretch()

        layout.addLayout(actions_row)

        # Пока только заглушка под канбан
        title = QLabel("Канбан-доска проекта")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        layout.addWidget(title)

        placeholder = QLabel(
            "Здесь будет канбан-доска с задачами этого проекта.\n"
            "Сейчас реализована только верстка страницы проекта."
        )
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #666666; font-size: 14px;")
        layout.addWidget(placeholder, stretch=1)

        return content

    # ----- Data loading -----

    def _load_data(self):
        """Загрузить детали проекта и участников и отобразить их в шапке."""
        try:
            self.project = projects_api.get_project_details(self.project_id, self.auth_service.token)
            self.members = projects_api.get_project_members(self.project_id, self.auth_service.token)

            self._update_header_info()
        except Exception as e:
            print(f"Error loading project {self.project_id}: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить проект: {e}")

    def _update_header_info(self):
        if not self.project:
            return

        self.project_name_label.setText(self.project.Name)

        participants_count = len(self.members)
        # Количество задач пока не считаем — оставим 0
        tasks_count = 0

        self.meta_label.setText(
            f"Задач: {tasks_count} • Участников: {participants_count}"
        )
        self.participants_label.setText(f"Участники: {participants_count}")

    # ----- Events -----

    def _on_avatar_clicked(self, event: QMouseEvent):
        if self.dropdown.isVisible():
            self.dropdown.hide()
        else:
            avatar_global_pos = self.avatar_label.mapToGlobal(QPoint(0, 0))
            dropdown_x = avatar_global_pos.x() - self.dropdown.width() + self.avatar_label.width()
            dropdown_y = avatar_global_pos.y() + self.avatar_label.height() + 5

            self.dropdown.move(dropdown_x, dropdown_y)
            self.dropdown.show()
        event.accept()

    def _open_members_dialog(self):
        dialog = ProjectMembersDialog(self)
        dialog.exec()

    def _open_roles_dialog(self):
        dialog = ProjectRolesDialog(self)
        dialog.exec()


