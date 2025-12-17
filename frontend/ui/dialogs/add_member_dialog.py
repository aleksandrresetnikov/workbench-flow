from typing import List, Optional

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QWidget,
)

from api.dtos import (
    ProjectDTO,
    ProjectMemberCreateDTO,
    ProjectMemberWithUserDTO,
    ProjectMemberDTO,
)
from api.projects import projects_api
from services.auth_service import AuthService
from ui.components import ModalCard, FieldLabel, PrimaryButton


class AddMemberDialog(QDialog):
    """Диалог добавления участника в проект."""

    member_added = Signal(ProjectMemberWithUserDTO)

    def __init__(
        self,
        project: ProjectDTO,
        auth_service: AuthService,
        members: List[ProjectMemberWithUserDTO],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.project = project
        self.auth_service = auth_service
        self.members = members
        self._selected_user_id: Optional[int] = None
        self._users_index = {m.member.Id: m.member for m in members}

        self.setWindowTitle("Добавить участника")
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        card = ModalCard()
        card.setFixedWidth(450)

        title = QLabel("Добавить участника")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        card.layout.addWidget(title)

        # Assignee search
        card.layout.addWidget(FieldLabel("Ответственный (поиск по email)"))
        self.user_input = QLineEdit()
        self.user_input.setObjectName("InputField")
        self.user_input.setPlaceholderText("Введите email пользователя")
        self.user_input.textChanged.connect(self._update_suggestions)
        card.layout.addWidget(self.user_input)

        self.suggestions = QListWidget()
        self.suggestions.setObjectName("MemberSuggestions")
        self.suggestions.itemClicked.connect(self._on_suggestion_clicked)
        self.suggestions.setVisible(False)
        card.layout.addWidget(self.suggestions)

        # Role
        card.layout.addWidget(FieldLabel("Роль участника в проекте"))
        self.role_combo = QComboBox()
        self.role_combo.addItem("Участник", "Common")
        self.role_combo.addItem("Админ", "Admin")
        card.layout.addWidget(self.role_combo)

        create_btn = PrimaryButton("Создать")
        create_btn.setFixedHeight(50)
        create_btn.clicked.connect(self._on_create_clicked)
        card.layout.addWidget(create_btn)

        layout.addWidget(card)

    # ---------- Suggestions ----------
    def _update_suggestions(self, text: str) -> None:
        self.suggestions.clear()
        text = text.strip().lower()
        if not text:
            self.suggestions.setVisible(False)
            self._selected_user_id = None
            return

        for member in self.members:
            user = member.member
            haystack = f"{user.Username} {user.Email}".lower()
            if text in haystack:
                item = QListWidgetItem(f"{user.Username} ({user.Email})")
                item.setData(Qt.UserRole, user.Id)
                self.suggestions.addItem(item)

        self.suggestions.setVisible(self.suggestions.count() > 0)

    def _on_suggestion_clicked(self, item: QListWidgetItem) -> None:
        user_id = item.data(Qt.UserRole)
        self._selected_user_id = user_id
        user = self._users_index.get(user_id)
        if user:
            self.user_input.setText(user.Email)
        self.suggestions.setVisible(False)

    # ---------- Create ----------
    def _on_create_clicked(self) -> None:
        if not self._selected_user_id:
            QMessageBox.warning(self, "Ошибка валидации", "Выберите пользователя из списка.")
            return

        role = self.role_combo.currentData()
        data = ProjectMemberCreateDTO(MemnerId=self._selected_user_id, Role=role)

        try:
            token = self.auth_service.token
            if not token:
                raise RuntimeError("Отсутствует токен авторизации")
            member_dto: ProjectMemberDTO = projects_api.add_project_member(self.project.Id, data, token)

            # Оборачиваем в ProjectMemberWithUserDTO, используя уже известного пользователя
            user = self._users_index.get(member_dto.MemnerId)
            combined = ProjectMemberWithUserDTO(
                Id=member_dto.Id,
                ProjectId=member_dto.ProjectId,
                MemnerId=member_dto.MemnerId,
                Role=member_dto.Role,
                CreateDate=member_dto.CreateDate,
                member=user,
            )
            self.member_added.emit(combined)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить участника: {e}")


