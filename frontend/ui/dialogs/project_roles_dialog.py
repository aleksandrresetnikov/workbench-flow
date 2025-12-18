from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class ProjectRolesDialog(QDialog):
    """Диалог управления ролями участников (пока заглушка)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Роли участников")
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        label = QLabel(
            "Здесь будет управление ролями участников проекта (Admin / Common и др.)."
        )
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop)
        layout.addWidget(label)


