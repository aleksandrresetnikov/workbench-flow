from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QWidget,
)

from api.dtos import ProjectDTO, ProjectMemberWithUserDTO
from ui.components import ModalCard, FieldLabel


class MembersListDialog(QDialog):
    """Диалог просмотра списка участников проекта."""

    def __init__(
        self,
        project: ProjectDTO,
        members: List[ProjectMemberWithUserDTO],
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        self.project = project
        self.members = members

        self.setWindowTitle("Участники проекта")
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

        title = QLabel("Участники проекта")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        card.layout.addWidget(title)

        card.layout.addWidget(FieldLabel("Список участников"))

        self.list_widget = QListWidget()
        for member in self.members:
            user = member.member
            text = f"{user.Username} ({user.Email}) — {member.Role}"
            QListWidgetItem(text, self.list_widget)

        card.layout.addWidget(self.list_widget)

        layout.addWidget(card)


