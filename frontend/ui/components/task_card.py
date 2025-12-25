from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QFont, QPixmap, QMouseEvent

from api.dtos import TaskDTO
from ui.components.dropdown import TaskGroupDropdown


import random

TAG_COLORS = {
    "Дизайн": "#1F3A5F",
    "Баг": "#8B1E3F",
    "UX": "#2D6A4F",
    "Нововведение": "#5A4FCF",
    # extra colors for variety
    "Орфография": "#D9480F",
    "Приоритет": "#0B84A5",
}


class TaskCard(QFrame):
    group_changed = Signal(int, int)  # task_id, new_group_id
    completed = Signal(int)  # task_id

    def __init__(self, task: TaskDTO, groups: list, parent=None):
        super().__init__(parent)
        self.task = task
        self.groups = groups
        # Keep references to tag widgets so we can update their styles when task completes
        self._tag_labels = []
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("TaskCard")
        self.setStyleSheet("""
            QFrame#TaskCard {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E6E6E6;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # ---- Title ----
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel(self.task.Name)
        title.setFont(QFont("Arial", 11, QFont.Bold))
        title.setStyleSheet("color: #1C1C1C;")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        
        # Three dots icon
        self.more_btn = QPushButton()
        self.more_btn.setObjectName("MoreButton")
        self.more_btn.setFixedSize(20, 20)
        self.more_btn.setCursor(Qt.PointingHandCursor)
        try:
            pixmap = QPixmap("resources/more_icon.png")
            if not pixmap.isNull():
                pixmap = pixmap.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.more_btn.setIcon(pixmap)
        except:
            self.more_btn.setText("⋮")  # Fallback text
        self.more_btn.clicked.connect(self.on_more_clicked)
        title_layout.addWidget(self.more_btn)
        
        layout.addLayout(title_layout)

        # ---- Description ----
        if self.task.Description:
            desc = QLabel(self.task.Description)
            desc.setWordWrap(True)
            desc.setStyleSheet("color: #666666; font-size: 12px;")
            layout.addWidget(desc)

        # ---- Bottom line: Deadline (left) and ownership indicator (right) ----
        self.bottom_row = QHBoxLayout()
        self.bottom_row.setContentsMargins(0, 6, 0, 0)
        self.bottom_row.setSpacing(8)

        # Left: deadline (handle date/datetime/ISO-string)
        dl_value = getattr(self.task, 'Deadline', None)
        if dl_value:
            try:
                formatted = dl_value.strftime('%d.%m.%Y')
            except Exception:
                # Fallback parse ISO string
                from datetime import datetime as _dt
                try:
                    parsed = _dt.fromisoformat(str(dl_value))
                    formatted = parsed.strftime('%d.%m.%Y')
                except Exception:
                    formatted = str(dl_value)
            dl_label = QLabel(f"Дедлайн: {formatted}")
            dl_label.setStyleSheet("color: #FF6B6B; font-size: 10px; font-weight: bold;")
            self.bottom_row.addWidget(dl_label)
        else:
            self.bottom_row.addWidget(QLabel(""))

        self.bottom_row.addStretch()

        # Right: ownership indicator if task assigned to current user
        self.owner_label = None
        try:
            from services import auth_service
            current = auth_service.current_user
            if current and getattr(self.task, 'TargetId', None) == getattr(current, 'Id', None):
                self.owner_label = QLabel("Ваша")
                self.owner_label.setStyleSheet("""
                    QLabel {
                        background-color: #0B84A5;
                        color: #FFFFFF;
                        border-radius: 6px;
                        padding: 2px 8px;
                        font-size: 10px;
                    }
                """)
        except Exception:
            self.owner_label = None

        if self.owner_label:
            self.owner_label.setAlignment(Qt.AlignCenter)
            self.bottom_row.addWidget(self.owner_label)

        layout.addLayout(self.bottom_row)

        # ---- Tags ----
        tags_row = QHBoxLayout()
        tags_row.setSpacing(6)

        # Use Tags from backend if present (comma-separated), otherwise fall back to Status
        raw_tags = getattr(self.task, 'Tags', None) or ''
        tags = [t for t in raw_tags.split(',') if t] if raw_tags else []
        if not tags:
            tags = [self.task.Status or "Общее"]

        for t in tags:
            tag = QLabel(t)
            tag.setAlignment(Qt.AlignCenter)
            color = TAG_COLORS.get(t, random.choice(list(TAG_COLORS.values())))
            tag.setStyleSheet(f"""
                QLabel {{
                    background-color: {color};
                    color: #FFFFFF;
                    border-radius: 6px;
                    padding: 2px 8px;
                    font-size: 11px;
                }}
            """)
            tags_row.addWidget(tag)
            # store for later updates when task state changes
            self._tag_labels.append(tag)

        tags_row.addStretch()
        layout.addLayout(tags_row)

        # If task is already closed, show completed indicator
        if getattr(self.task, 'IsClosed', False):
            self._render_completed_state()

    def on_more_clicked(self):
        """Handle three-dots button click"""
        if not hasattr(self, 'dropdown'):
            self.dropdown = TaskGroupDropdown(self.groups, self.task.GroupId, self)
            self.dropdown.group_selected.connect(self.on_group_selected)
        
        # Position dropdown below the button
        btn_global_pos = self.more_btn.mapToGlobal(QPoint(0, 0))
        dropdown_x = btn_global_pos.x() - self.dropdown.width() + self.more_btn.width()
        dropdown_y = btn_global_pos.y() + self.more_btn.height() + 5
        
        self.dropdown.move(dropdown_x, dropdown_y)
        self.dropdown.show()
    
    def on_group_selected(self, group_id: int):
        """Handle group selection from dropdown"""
        self.dropdown.hide()
        self.group_changed.emit(self.task.Id, group_id)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Open task info dialog when card is clicked (but not when clicking the more button)"""
        if event.button() == Qt.LeftButton:
            try:
                child = self.childAt(event.pos())
                # If clicked on the more button, don't open the dialog
                if child is self.more_btn or (hasattr(child, 'objectName') and child.objectName() == 'MoreButton'):
                    super().mouseReleaseEvent(event)
                    return

                from ui.dialogs.task_info_dialog import TaskInfoDialog
                dialog = TaskInfoDialog(self.task, self)
                dialog.task_completed.connect(self._on_task_completed)
                dialog.exec()
            except Exception as e:
                print(f"Failed to open task dialog: {e}")

        super().mouseReleaseEvent(event)

    def _render_completed_state(self):
        # Add a 'Completed' badge to the right side
        if not hasattr(self, '_completed_label'):
            self._completed_label = QLabel("Выполнено")
            self._completed_label.setStyleSheet("""
                QLabel {
                    background-color: #E5F6F8;
                    color: #0B84A5;
                    border-radius: 6px;
                    padding: 2px 8px;
                    font-size: 10px;
                }
            """)
            self._completed_label.setAlignment(Qt.AlignCenter)
            self.bottom_row.addWidget(self._completed_label)

        # Slightly dim the card to indicate completion
        self.setStyleSheet("""
            QFrame#TaskCard {
                background-color: #F7F7F7;
                border-radius: 10px;
                border: 1px solid #E6E6E6;
                color: #999999;
            }
        """)

        # Dim tags so they don't stand out on a completed card
        for tag in getattr(self, '_tag_labels', []):
            try:
                tag.setStyleSheet("""
                    QLabel {
                        background-color: #D9D9D9;
                        color: #666666;
                        border-radius: 6px;
                        padding: 2px 8px;
                        font-size: 11px;
                    }
                """)
            except Exception:
                pass

        # Dim owner label if present
        if getattr(self, 'owner_label', None):
            try:
                self.owner_label.setStyleSheet("""
                    QLabel {
                        background-color: #C4C4C4;
                        color: #666666;
                        border-radius: 6px;
                        padding: 2px 8px;
                        font-size: 10px;
                    }
                """)
            except Exception:
                pass

        # Notify listeners that this task is now completed
        try:
            print(f"[UI] TaskCard {getattr(self.task, 'Id', '?')} rendered completed state")
            self.completed.emit(self.task.Id)
        except Exception:
            pass

    def _on_task_completed(self, task_id: int):
        try:
            if task_id == self.task.Id:
                self.task.IsClosed = True
                self._render_completed_state()
                # Also emit completed for parent boards to react
                try:
                    self.completed.emit(self.task.Id)
                except Exception:
                    pass
        except Exception as e:
            print(f"Error applying completed state: {e}")