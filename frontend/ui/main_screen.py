# Main Screen
# Projects page displaying user's projects with management features

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, 
    QLineEdit, QTextEdit, QDateEdit, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPixmap, QFont, QMouseEvent

from services.auth_service import AuthService
from api.projects import projects_api
from api.dtos import ProjectCreateDTO, ProjectDTO
from ui.components import CreateProjectButton, PrimaryButton, FieldLabel, ModalCard, UserDropdown

def translate_role(role: str, is_owner: bool = False) -> str:
    """Translate role to Russian"""
    if is_owner:
        return "Владелец"
    role_map = {
        "Admin": "Админ",
        "Common": "Участник",
        "admin": "Админ",
        "common": "Участник",
    }
    return role_map.get(role, role)

class MainScreen(QWidget):
    """Main screen displaying projects list with header and create functionality"""
    logout_requested = Signal()
    project_open_requested = Signal(int)

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.setup_ui()
        self.load_projects()

    def setup_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Header
        self.header = self.create_header()
        self.layout.addWidget(self.header)

        # Projects table
        self.table = self.create_projects_table()
        self.layout.addWidget(self.table)

        self.table.cellDoubleClicked.connect(self.handle_project_double_click)

    def create_header(self) -> QWidget:
        """Create the top header with title, user info, and create button"""
        header_widget = QWidget()
        header_widget.setObjectName("HeaderWidget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(30, 20, 30, 20)
        header_layout.setSpacing(20)

        # App title
        title = QLabel("Workbench Flow")
        title.setObjectName("HeaderLabel")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Create Project button (moved before user info)
        create_btn = CreateProjectButton()
        create_btn.clicked.connect(self.show_create_dialog)
        header_layout.addWidget(create_btn)

        # User info section
        user_widget = QWidget()
        user_widget.setObjectName("UserWidget")
        user_layout = QHBoxLayout(user_widget)
        user_layout.setSpacing(12)
        user_layout.setContentsMargins(0, 0, 0, 0)

        # User details
        user_info = QWidget()
        user_info_layout = QVBoxLayout(user_info)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(2)

        # Name
        name = f"{self.auth_service.current_user.FirstName or ''} {self.auth_service.current_user.LastName or ''}".strip()
        if not name:
            name = self.auth_service.current_user.Username
        name_label = QLabel(name)
        name_label.setObjectName("UserLabel")
        name_label.setStyleSheet("font-size: 14px; color: #FFFFFF;")
        user_info_layout.addWidget(name_label)

        # Email
        email_label = QLabel(self.auth_service.current_user.Email)
        email_label.setObjectName("UserLabel")
        email_label.setStyleSheet("font-size: 12px; color: #D1E9FF;")
        user_info_layout.addWidget(email_label)

        user_layout.addWidget(user_info)

        # Avatar (clickable)
        self.avatar_label = QLabel()
        self.avatar_label.setCursor(Qt.PointingHandCursor)
        try:
            pixmap = QPixmap("resources/profile_no_avatar.png")
            if not pixmap.isNull():
                pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.avatar_label.setPixmap(pixmap)
        except:
            pass
        self.avatar_label.setFixedSize(40, 40)
        self.avatar_label.mousePressEvent = self.on_avatar_clicked
        user_layout.addWidget(self.avatar_label)

        header_layout.addWidget(user_widget)

        # Dropdown (initially hidden)
        self.dropdown = UserDropdown(self)
        self.dropdown.hide()
        self.dropdown.logout_requested.connect(self.handle_logout)

        return header_widget

    def create_projects_table(self) -> QTableWidget:
        """Create the projects table widget"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["#", "НАИМЕНОВАНИЕ", "ОПИСАНИЕ", "РОЛЬ", "УЧАСТНИКИ"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setObjectName("ProjectsTable")
        table.verticalHeader().setDefaultSectionSize(60)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # #
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Description
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Role
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Participants
        
        # Style header
        header.setDefaultSectionSize(50)
        header.setFont(QFont("Arial", 12, QFont.Bold))
        
        return table

    def load_projects(self):
        """Load and display user's projects"""
        try:
            self.projects = projects_api.get_my_projects(self.auth_service.token)
            self.table.setRowCount(len(self.projects))

            for i, project in enumerate(self.projects):
                # Index
                index_item = QTableWidgetItem(str(i + 1))
                index_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 0, index_item)

                # Project Name with ID
                name_widget = QWidget()
                name_widget.setStyleSheet("background-color: transparent;")
                name_layout = QVBoxLayout(name_widget)
                name_layout.setContentsMargins(8, 4, 8, 4)
                name_layout.setSpacing(2)
                
                name_label = QLabel(project.Name)
                name_label.setStyleSheet("background-color: transparent; font-weight: bold; color: #000000;")
                name_layout.addWidget(name_label)
                
                id_label = QLabel(str(project.Id))
                id_label.setStyleSheet("background-color: transparent; font-size: 12px; color: #666666;")
                name_layout.addWidget(id_label)
                
                self.table.setCellWidget(i, 1, name_widget)

                # Description
                desc = project.Description or "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla..."
                desc_item = QTableWidgetItem(desc)
                desc_item.setToolTip(desc)
                self.table.setItem(i, 2, desc_item)

                # Role and Participants
                try:
                    members = projects_api.get_project_members(project.Id, self.auth_service.token)
                    user_member = next((m for m in members if m.MemnerId == self.auth_service.current_user.Id), None)
                    is_owner = project.OwnerId == self.auth_service.current_user.Id
                    role = translate_role(user_member.Role if user_member else "Common", is_owner)
                    participants = len(members)
                except Exception as e:
                    print(f"Error fetching members for project {project.Id}: {e}")
                    role = "Участник"
                    participants = 0
                    is_owner = False

                # Role badge
                role_button = QPushButton(role)
                role_button.setObjectName("RoleBadge")
                role_button.setEnabled(False)
                role_button.setCursor(Qt.ArrowCursor)
                # Allow text to wrap or use elided text if needed
                role_button.setText(role)
                self.table.setCellWidget(i, 3, role_button)

                # Participants
                participants_item = QTableWidgetItem(str(participants))
                participants_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, 4, participants_item)

        except Exception as e:
            print(f"Error loading projects: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить проекты: {e}")

    def handle_project_double_click(self, row: int, column: int):
        """Open project screen on row double click"""
        if not hasattr(self, "projects"):
            return
        if row < 0 or row >= len(self.projects):
            return
        project = self.projects[row]
        self.project_open_requested.emit(project.Id)

    def show_create_dialog(self):
        """Show the create project dialog"""
        dialog = CreateProjectDialog(self.auth_service)
        dialog.project_created.connect(self.on_project_created)
        dialog.exec()

    def on_project_created(self, project: ProjectDTO):
        """Handle project creation success"""
        self.load_projects()

    def on_avatar_clicked(self, event: QMouseEvent):
        """Handle avatar click to show/hide dropdown"""
        if self.dropdown.isVisible():
            self.dropdown.hide()
        else:
            # Calculate dropdown position (below avatar, aligned to right)
            avatar_global_pos = self.avatar_label.mapToGlobal(QPoint(0, 0))
            
            # Position dropdown in global coordinates (since it's a popup)
            dropdown_x = avatar_global_pos.x() - self.dropdown.width() + self.avatar_label.width()
            dropdown_y = avatar_global_pos.y() + self.avatar_label.height() + 5
            
            self.dropdown.move(dropdown_x, dropdown_y)
            self.dropdown.show()
        event.accept()
    
    def handle_logout(self):
        """Handle logout button click"""
        self.dropdown.hide()
        self.logout_requested.emit()


class CreateProjectDialog(QDialog):
    """Dialog for creating a new project"""
    project_created = Signal(ProjectDTO)

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("Новый проект")
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: rgba(0, 0, 0, 0.5); }")
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Modal card
        card = ModalCard()
        card.setFixedWidth(550)

        # Title
        title = QLabel("Новый проект")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("color: #000000; font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        card.layout.addWidget(title)

        # Project Name
        name_label = FieldLabel("Наименование")
        card.layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setObjectName("InputField")
        self.name_input.setPlaceholderText("Введите наименование проекта")
        self.name_input.setFixedHeight(50)
        card.layout.addWidget(self.name_input)

        # Description
        desc_label = FieldLabel("Описание")
        card.layout.addWidget(desc_label)
        
        self.desc_input = QTextEdit()
        self.desc_input.setObjectName("TextEdit")
        self.desc_input.setPlaceholderText("Введите описание проекта")
        self.desc_input.setMaximumHeight(100)
        card.layout.addWidget(self.desc_input)

        # Deadline (optional)
        deadline_label = FieldLabel("Сроки выполнения")
        card.layout.addWidget(deadline_label)
        
        self.deadline_input = QDateEdit()
        self.deadline_input.setObjectName("DateEdit")
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setFixedHeight(50)
        card.layout.addWidget(self.deadline_input)

        # Create button
        create_button = PrimaryButton("Создать")
        create_button.setFixedHeight(50)
        create_button.clicked.connect(self.accept)
        card.layout.addWidget(create_button)

        layout.addWidget(card)

    def accept(self):
        """Handle create button click"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка валидации", "Наименование проекта обязательно.")
            return

        desc = self.desc_input.toPlainText().strip()
        # Deadline not implemented in API yet

        data = ProjectCreateDTO(Name=name, Description=desc or None)

        try:
            project = projects_api.create_project(data, self.auth_service.token)
            self.project_created.emit(project)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать проект: {e}")
