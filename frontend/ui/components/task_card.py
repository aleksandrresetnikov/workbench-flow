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

    def __init__(self, task: TaskDTO, groups: list, parent=None):
        super().__init__(parent)
        self.task = task
        self.groups = groups
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
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 6, 0, 0)
        bottom_row.setSpacing(8)

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
            bottom_row.addWidget(dl_label)
        else:
            bottom_row.addWidget(QLabel(""))

        bottom_row.addStretch()

        # Right: ownership indicator if task assigned to current user
        owner_label = None
        try:
            from services import auth_service
            current = auth_service.current_user
            if current and getattr(self.task, 'TargetId', None) == getattr(current, 'Id', None):
                owner_label = QLabel("Ваша")
                owner_label.setStyleSheet("""
                    QLabel {
                        background-color: #0B84A5;
                        color: #FFFFFF;
                        border-radius: 6px;
                        padding: 2px 8px;
                        font-size: 10px;
                    }
                """)
        except Exception:
            owner_label = None

        if owner_label:
            owner_label.setAlignment(Qt.AlignCenter)
            bottom_row.addWidget(owner_label)

        layout.addLayout(bottom_row)

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

        tags_row.addStretch()
        layout.addLayout(tags_row)

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