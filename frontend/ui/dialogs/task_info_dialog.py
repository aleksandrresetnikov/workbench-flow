from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt, Signal
from ui.components import ModalCard, PrimaryButton, SecondaryButton

from services import auth_service
from api.tasks import tasks_api
from api.dtos import TaskUpdateDTO, TaskDTO


class TaskInfoDialog(QDialog):
    task_completed = Signal(int)  # task id

    def __init__(self, task: TaskDTO, parent=None):
        super().__init__(parent)
        self.task = task
        self.setWindowTitle("Информация о задаче")
        self.setModal(True)
        self.setFixedSize(560, 360)

        self._setup_ui()
        # Ensure we have latest status from API when opening
        self._refresh_task()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignCenter)

        card = ModalCard()
        card.setFixedWidth(520)
        card.layout.setSpacing(12)

        # Title
        self.title_label = QLabel(self.task.Name)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        card.layout.addWidget(self.title_label)

        # Description
        self.desc_label = QLabel(self.task.Description or "(Нет описания)")
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet("color: #333333; font-size: 13px;")
        card.layout.addWidget(self.desc_label)

        # Status line
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #555555; font-size: 12px;")
        card.layout.addWidget(self.status_label)

        # Buttons
        buttons = QHBoxLayout()
        buttons.setSpacing(12)

        self.close_btn = SecondaryButton("Закрыть")
        self.close_btn.clicked.connect(self.reject)
        buttons.addWidget(self.close_btn)

        # Complete button only present when task is open; created but hidden for now
        self.complete_btn = PrimaryButton("Выполнить")
        self.complete_btn.clicked.connect(self._on_complete_clicked)
        buttons.addWidget(self.complete_btn)

        card.layout.addLayout(buttons)
        root.addWidget(card)

    def _refresh_task(self):
        try:
            # Fetch latest task details to get IsClosed if missing
            token = getattr(auth_service, 'token', None)
            if token is not None:
                updated = tasks_api.get_task(self.task.Id, token)
                # Update task and ui
                self.task = updated
            self._update_ui()
        except Exception as e:
            # If refreshing failed, still show existing info
            print(f"Failed to refresh task: {e}")
            self._update_ui()

    def _update_ui(self):
        self.title_label.setText(self.task.Name)
        self.desc_label.setText(self.task.Description or "(Нет описания)")

        is_closed = getattr(self.task, 'IsClosed', False)
        if is_closed:
            self.status_label.setText("Статус: Выполнено")
            self.complete_btn.setVisible(False)
        else:
            self.status_label.setText("Статус: Открыта")
            self.complete_btn.setVisible(True)

    def _on_complete_clicked(self):
        try:
            print(f"[UI] Completing task {self.task.Id} - sending update to API")
            token = getattr(auth_service, 'token', None)
            if token is None:
                raise Exception("Нет токена авторизации")
            upd = TaskUpdateDTO(IsClosed=True)
            updated_task = tasks_api.update_task(self.task.Id, upd, token)
            # Update internal task representation
            self.task = updated_task

            # Use a small ModalCard dialog for confirmation so styling is consistent and text is visible
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel
            from ui.components import PrimaryButton

            confirm = QDialog(self)
            confirm.setWindowTitle("Готово")
            confirm.setModal(True)
            confirm.setFixedSize(360, 160)
            layout = QVBoxLayout(confirm)
            layout.setContentsMargins(20, 20, 20, 20)
            msg = QLabel("Задача помечена как выполненной")
            msg.setStyleSheet("color: #000000; font-size: 14px;")
            layout.addWidget(msg)
            ok = PrimaryButton("OK")
            ok.clicked.connect(confirm.accept)
            layout.addWidget(ok)
            print(f"[UI] Showing confirmation dialog for task {self.task.Id}")
            confirm.exec()

            # Notify listeners
            self.task_completed.emit(self.task.Id)
            print(f"[UI] Emitted task_completed for {self.task.Id}")
            self.accept()
        except Exception as e:
            print(f"[UI] Failed to complete task {self.task.Id}: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось пометить задачу выполненной: {e}")
