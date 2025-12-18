from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class ProjectMembersDialog(QDialog):
    """Диалог со списком участников проекта (пока заглушка)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Участники проекта")
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        label = QLabel(
            "Здесь будет список участников проекта с возможностью управления доступом."
        )
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop)
        layout.addWidget(label)


