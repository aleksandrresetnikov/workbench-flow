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
from typing import Optional, List

from services.auth_service import AuthService
from api.projects import projects_api
from api.task_groups import task_groups_api
from api.tasks import tasks_api
from api.dtos import ProjectWithDetailsDTO, ProjectMemberWithUserDTO, TaskGroupDTO, TaskDTO
from ui.components import UserDropdown, PrimaryButton, SecondaryButton
from ui.components.kanban_board import KanbanBoard
from ui.dialogs.project_members_dialog import ProjectMembersDialog
from ui.dialogs.project_roles_dialog import ProjectRolesDialog
from ui.dialogs.project_task_groups_dialog import ProjectTaskGroupsDialog
from ui.dialogs.create_task_dialog import CreateTaskDialog


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

        self.project: Optional[ProjectWithDetailsDTO] = None
        self.members: List[ProjectMemberWithUserDTO] = []
        self.task_groups: List[TaskGroupDTO] = []
        self.tasks: List[TaskDTO] = []
        self.is_admin: bool = False

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

        self.add_task_btn = PrimaryButton("Новая задача")
        self.add_task_btn.setFixedHeight(40)
        self.add_task_btn.setEnabled(False)  # включим после успешной загрузки проекта
        self.add_task_btn.clicked.connect(self._open_create_task_dialog)
        actions_row.addWidget(self.add_task_btn)

        self.members_btn = SecondaryButton("Участники проекта")
        self.members_btn.setFixedHeight(40)
        self.members_btn.setEnabled(False)  # включим для админов после загрузки данных
        self.members_btn.clicked.connect(self._open_members_dialog)
        actions_row.addWidget(self.members_btn)

        self.roles_btn = SecondaryButton("Роли участников")
        self.roles_btn.setFixedHeight(40)
        self.roles_btn.setEnabled(False)  # включим для админов после загрузки данных
        self.roles_btn.clicked.connect(self._open_roles_dialog)
        actions_row.addWidget(self.roles_btn)

        self.groups_btn = SecondaryButton("Группы задач")
        self.groups_btn.setFixedHeight(40)
        self.groups_btn.setEnabled(False)
        self.groups_btn.clicked.connect(self._open_groups_dialog)
        actions_row.addWidget(self.groups_btn)

        actions_row.addStretch()

        layout.addLayout(actions_row)

        # Область для канбан-доски
        self.kanban_area = QWidget()
        kanban_layout = QVBoxLayout(self.kanban_area)
        kanban_layout.setContentsMargins(0, 0, 0, 0)
        kanban_layout.setSpacing(0)

        # Заглушка до загрузки данных
        placeholder = QLabel("Загрузка канбан-доски...")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #666666; font-size: 14px;")
        kanban_layout.addWidget(placeholder)

        layout.addWidget(self.kanban_area, stretch=1)

        return content

    # ----- Data loading -----

    def _load_data(self):
        """Загрузить детали проекта и участников и отобразить их в шапке."""
        try:
            self.project = projects_api.get_project_details(self.project_id, self.auth_service.token)
            self.members = projects_api.get_project_members(self.project_id, self.auth_service.token)
            self.task_groups = task_groups_api.get_task_groups_for_project(self.project_id, self.auth_service.token)
            self.tasks = tasks_api.get_tasks(self.project_id, self.auth_service.token)

            self._update_header_info()
            self._update_content()
            self._bind_board_callbacks()
        except Exception as e:
            print(f"Error loading project {self.project_id}: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить проект: {e}")

    def _update_content(self):
        """Обновить содержимое канбан-доски после загрузки данных."""
        # Очистить текущий контент
        if self.kanban_area.layout():
            while self.kanban_area.layout().count():
                child = self.kanban_area.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Создать канбан-доску (передаём callback для кнопки '+' в колонках)
        self.kanban_board = KanbanBoard(self.task_groups, self.tasks, on_add_task=self._open_create_task_dialog_with_group)
        self.kanban_area.layout().addWidget(self.kanban_board)

    def _update_header_info(self):
        if not self.project:
            return

        self.project_name_label.setText(self.project.Name)

        participants_count = len(self.members)
        # Количество задач
        tasks_count = len(self.tasks)

        self.meta_label.setText(
            f"Задач: {tasks_count} • Участников: {participants_count}"
        )
        self.participants_label.setText(f"Участники: {participants_count}")

        # Определяем, является ли текущий пользователь администратором проекта
        current_user_id = self.auth_service.current_user.Id
        is_owner = self.project.OwnerId == current_user_id
        user_member = next(
            (m for m in self.members if m.MemnerId == current_user_id), None
        )
        access_level = getattr(user_member, "AccessLevel", "Common") if user_member else "Common"

        self.is_admin = bool(is_owner or access_level == "Admin")
        self.members_btn.setEnabled(self.is_admin)
        self.roles_btn.setEnabled(self.is_admin)
        self.groups_btn.setEnabled(self.is_admin)

        # Разрешаем создавать задачи всем пользователям, если проект загружен и у пользователя есть доступ
        self.add_task_btn.setEnabled(True)

    def _update_content(self):
        """Обновить содержимое канбан-доски после загрузки данных."""
        # Очистить текущий контент
        if self.kanban_area.layout():
            while self.kanban_area.layout().count():
                child = self.kanban_area.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Создать канбан-доску (передаём callback для кнопки '+' в колонках)
        self.kanban_board = KanbanBoard(self.task_groups, self.tasks, on_add_task=self._open_create_task_dialog_with_group)
        self.kanban_area.layout().addWidget(self.kanban_board)

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

    def _move_task_to_group(self, task_id: int, group_id: int):
        """Move task to another group and refresh board"""
        try:
            tasks_api.move_task(task_id, group_id, self.auth_service.token)
            # refresh tasks from server
            self.tasks = tasks_api.get_tasks(self.project_id, self.auth_service.token)
            self._update_content()
            self._bind_board_callbacks()
        except Exception as e:
            print(f"Error moving task {task_id} to group {group_id}: {e}")
            QMessageBox.warning(self, "Ошибка", f"Не удалось переместить задачу: {e}")

    def _bind_board_callbacks(self):
        """Ensure board callbacks (e.g., move) are bound to the current board instance."""
        if hasattr(self, 'kanban_board') and self.kanban_board is not None:
            try:
                self.kanban_board.on_move_task = self._move_task_to_group
            except Exception:
                pass

    def _open_members_dialog(self):
        dialog = ProjectMembersDialog(
            auth_service=self.auth_service,
            project_id=self.project_id,
            parent=self,
        )
        dialog.exec()

    def _open_create_task_dialog(self):
        dialog = CreateTaskDialog(
            auth_service=self.auth_service,
            project_id=self.project_id,
            members=self.members,
            groups=self.task_groups,
            parent=self,
        )

        def on_task_created(task):
            # обновляем список задач и перерисовываем доску
            self.tasks.append(task)
            self._update_content()
            self._bind_board_callbacks()

        dialog.task_created.connect(on_task_created)
        dialog.exec()

    def _open_create_task_dialog_with_group(self, group_id: int):
        dialog = CreateTaskDialog(
            auth_service=self.auth_service,
            project_id=self.project_id,
            members=self.members,
            groups=self.task_groups,
            preselected_group_id=group_id,
            parent=self,
        )

        def on_task_created(task):
            self.tasks.append(task)
            self._update_content()
            self._bind_board_callbacks()

        dialog.task_created.connect(on_task_created)
        dialog.exec()

    def _open_roles_dialog(self):
        dialog = ProjectRolesDialog(
            auth_service=self.auth_service,
            project_id=self.project_id,
            parent=self,
        )
        dialog.exec()

    def _open_groups_dialog(self):
        dialog = ProjectTaskGroupsDialog(
            auth_service=self.auth_service,
            project_id=self.project_id,
            parent=self,
        )
        dialog.exec()

        # После закрытия диалога обновим локальные группы и перерисуем доску
        try:
            self.task_groups = task_groups_api.get_task_groups_for_project(self.project_id, self.auth_service.token)
            self.tasks = tasks_api.get_tasks(self.project_id, self.auth_service.token)
            self._update_content()
            self._bind_board_callbacks()
        except Exception as e:
            print(f"Error reloading groups/tasks: {e}")
            QMessageBox.warning(self, "Внимание", f"Не удалось обновить группы/задачи после изменений:\n{e}")


