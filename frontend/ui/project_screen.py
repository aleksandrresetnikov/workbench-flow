from collections import defaultdict
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QMessageBox,
)

from api.dtos import ProjectDTO, TaskDTO, TaskGroupDTO, ProjectMemberWithUserDTO
from api.projects import projects_api
from api.task_groups import task_groups_api
from api.tasks import tasks_api
from services.auth_service import AuthService
from ui.components import PrimaryButton, FieldLabel, LoadingOverlay
from ui.dialogs.new_task_dialog import NewTaskDialog
from ui.dialogs.new_group_dialog import NewTaskGroupDialog
from ui.dialogs.add_member_dialog import AddMemberDialog
from ui.dialogs.members_list_dialog import MembersListDialog


class KanbanCard(QFrame):
    """Карточка задачи в канбан-доске."""

    def __init__(self, task: TaskDTO, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.task = task
        self.setObjectName("KanbanCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title = QLabel(task.Name)
        title.setObjectName("KanbanCardTitle")
        title.setWordWrap(True)
        layout.addWidget(title)

        if task.Description:
            desc = QLabel(task.Description)
            desc.setObjectName("KanbanCardDescription")
            desc.setWordWrap(True)
            desc.setMaximumHeight(48)
            desc.setToolTip(task.Description)
            layout.addWidget(desc)


class KanbanColumn(QWidget):
    """Колонка (группа задач) на канбан-доске."""

    def __init__(self, group: Optional[TaskGroupDTO], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.group = group
        self.setObjectName("KanbanColumn")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # Заголовок колонки
        header = QHBoxLayout()
        header.setSpacing(8)

        name = QLabel(group.Name if group else "Без группы")
        name.setObjectName("KanbanColumnTitle")
        header.addWidget(name)

        header.addStretch()

        self.counter_label = QLabel("0")
        self.counter_label.setObjectName("KanbanColumnCounter")
        header.addWidget(self.counter_label)

        header_widget = QWidget()
        header_widget.setLayout(header)
        header_widget.setObjectName("KanbanColumnHeader")
        root_layout.addWidget(header_widget)

        # Область со скроллом для карточек
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.cards_layout = QVBoxLayout(content)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

    def set_tasks(self, tasks: List[TaskDTO]) -> None:
        """Обновить список карточек в колонке."""
        # Удаляем все виджеты, кроме завершающего stretch
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for task in tasks:
            card = KanbanCard(task, self)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

        self.counter_label.setText(str(len(tasks)))


class ProjectDataWorker(QThread):
    """Фоновая загрузка групп задач, задач и участников проекта."""

    data_loaded = Signal(list, list, list)
    error = Signal(str)

    def __init__(self, project_id: int, auth_service: AuthService):
        super().__init__()
        self._project_id = project_id
        self._auth_service = auth_service

    def run(self):
        try:
            token = self._auth_service.token
            if not token:
                raise RuntimeError("Отсутствует токен авторизации")

            groups = task_groups_api.get_task_groups_for_project(self._project_id, token)
            tasks = tasks_api.get_tasks(self._project_id, token)
            members = projects_api.get_project_members(self._project_id, token)
            self.data_loaded.emit(groups, tasks, members)
        except Exception as e:
            self.error.emit(str(e))


class ProjectScreen(QWidget):
    """
    Экран отдельного проекта с канбан-доской.
    Показывает группы задач (колонки), задачи и участников.
    """

    back_requested = Signal()

    def __init__(self, project: ProjectDTO, auth_service: AuthService, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.project = project
        self.auth_service = auth_service

        self._members: List[ProjectMemberWithUserDTO] = []
        self._groups: List[TaskGroupDTO] = []
        self._tasks: List[TaskDTO] = []
        self._columns: Dict[Optional[int], KanbanColumn] = {}
        self._data_worker: ProjectDataWorker | None = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.header = self._create_header()
        self.layout.addWidget(self.header)

        self.board_container = QWidget()
        self.board_layout = QHBoxLayout(self.board_container)
        self.board_layout.setContentsMargins(24, 24, 24, 24)
        self.board_layout.setSpacing(16)
        self.layout.addWidget(self.board_container)

        self.loading_overlay = LoadingOverlay(self.board_container, "Загружаем задачи")
        self.loading_overlay.hide()

        self._load_data()

    # ---------- UI ----------
    def _create_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("ProjectHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(16)

        # Левая часть: кнопка назад + название проекта
        left = QHBoxLayout()
        left.setSpacing(12)

        back_btn = QPushButton("←")
        back_btn.setObjectName("BackButton")
        back_btn.setFixedWidth(40)
        back_btn.clicked.connect(self.back_requested.emit)
        left.addWidget(back_btn)

        name_label = QLabel(self.project.Name)
        name_label.setObjectName("ProjectTitle")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        name_label.setFont(font)
        left.addWidget(name_label)

        # Счётчик задач
        self.tasks_count_label = QLabel("Задач 0")
        self.tasks_count_label.setObjectName("TasksCounter")
        left.addWidget(self.tasks_count_label)

        left_widget = QWidget()
        left_widget.setLayout(left)
        layout.addWidget(left_widget)

        layout.addStretch()

        # Правая часть: кнопки действий
        right = QHBoxLayout()
        right.setSpacing(12)

        # Кнопка список участников
        members_btn = QPushButton("Участники")
        members_btn.setObjectName("MembersButton")
        members_btn.clicked.connect(self._show_members_list)
        right.addWidget(members_btn)

        add_member_btn = PrimaryButton("+ Добавить участника")
        add_member_btn.clicked.connect(self._show_add_member_dialog)
        right.addWidget(add_member_btn)

        new_task_btn = PrimaryButton("Новая задача")
        new_task_btn.clicked.connect(self._show_new_task_dialog)
        right.addWidget(new_task_btn)

        new_group_btn = PrimaryButton("Новая группа")
        new_group_btn.clicked.connect(self._show_new_group_dialog)
        right.addWidget(new_group_btn)

        right_widget = QWidget()
        right_widget.setLayout(right)
        layout.addWidget(right_widget)

        return header

    # ---------- Data loading ----------
    def _load_data(self) -> None:
        """Запуск фоновой загрузки данных проекта."""
        self.loading_overlay.show()

        if self._data_worker is not None and self._data_worker.isRunning():
            self._data_worker.terminate()

        self._data_worker = ProjectDataWorker(self.project.Id, self.auth_service)
        self._data_worker.data_loaded.connect(self._on_data_loaded)
        self._data_worker.error.connect(self._on_data_error)
        self._data_worker.finished.connect(self.loading_overlay.hide)
        self._data_worker.start()

    def _on_data_loaded(
        self,
        groups: List[TaskGroupDTO],
        tasks: List[TaskDTO],
        members: List[ProjectMemberWithUserDTO],
    ) -> None:
        self._groups = groups
        self._tasks = tasks
        self._members = members
        self._rebuild_board()

    def _on_data_error(self, message: str) -> None:
        QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные проекта: {message}")

    def _rebuild_board(self) -> None:
        """Перестроить канбан-доску на основе текущих данных."""
        # Очистить layout и словарь колонок
        while self.board_layout.count():
            item = self.board_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._columns.clear()

        # Сначала колонка «Без группы» (для задач без GroupId)
        self._create_column_for_group(None)

        for group in self._groups:
            self._create_column_for_group(group.Id, group)

        # Разложить задачи по колонкам
        tasks_by_group: Dict[Optional[int], List[TaskDTO]] = defaultdict(list)
        for task in self._tasks:
            tasks_by_group[task.GroupId].append(task)

        total_tasks = len(self._tasks)
        self.tasks_count_label.setText(f"Задач {total_tasks}")

        for group_id, column in self._columns.items():
            column_tasks = tasks_by_group.get(group_id, [])
            column.set_tasks(column_tasks)

    def _create_column_for_group(self, group_id: Optional[int], group: Optional[TaskGroupDTO] = None) -> None:
        column = KanbanColumn(group, self.board_container)
        self.board_layout.addWidget(column)
        self._columns[group_id] = column

    # ---------- Dialogs ----------
    def _show_new_task_dialog(self) -> None:
        dialog = NewTaskDialog(self.project, self.auth_service, self._members, self)
        dialog.task_created.connect(self._on_task_created)
        dialog.exec()

    def _show_new_group_dialog(self) -> None:
        dialog = NewTaskGroupDialog(self.project, self.auth_service, self)
        dialog.group_created.connect(self._on_group_created)
        dialog.exec()

    def _show_add_member_dialog(self) -> None:
        dialog = AddMemberDialog(self.project, self.auth_service, self._members, self)
        dialog.member_added.connect(self._on_member_added)
        dialog.exec()

    def _show_members_list(self) -> None:
        dialog = MembersListDialog(self.project, self._members, self)
        dialog.exec()

    # ---------- Handlers ----------
    def _on_task_created(self, task: TaskDTO) -> None:
        self._tasks.append(task)
        self._rebuild_board()

    def _on_group_created(self, group: TaskGroupDTO) -> None:
        self._groups.append(group)
        self._rebuild_board()

    def _on_member_added(self, member: ProjectMemberWithUserDTO) -> None:
        self._members.append(member)


