# Main Screen
# Projects page displaying user's projects with management features

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QLineEdit, QTextEdit, QDateEdit, QDialogButtonBox, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

# Import color constants from centralized styles
from ui.styles.colors import PRIMARY, WHITE, MUTED

from services.auth_service import AuthService
from api.projects import projects_api
from api.dtos import ProjectCreateDTO, ProjectDTO

class MainScreen(QWidget):
    """Main screen displaying projects list with header and create functionality"""
    logout_requested = Signal()

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

    def create_header(self) -> QWidget:
        """Create the top header with title, user info, and create button"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)

        # App title
        title = QLabel("Workbench Flow")
        title.setObjectName("HeaderLabel")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # User info section
        user_widget = QWidget()
        user_layout = QHBoxLayout(user_widget)
        user_layout.setSpacing(10)

        # Avatar
        avatar = QLabel()
        pixmap = QPixmap("resources/profile_no_avatar.png").scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        avatar.setPixmap(pixmap)
        user_layout.addWidget(avatar)

        # User details
        user_info = QWidget()
        user_info_layout = QVBoxLayout(user_info)
        user_info_layout.setContentsMargins(0, 0, 0, 0)

        # Name
        name = f"{self.auth_service.current_user.FirstName or ''} {self.auth_service.current_user.LastName or ''}".strip()
        if not name:
            name = self.auth_service.current_user.Username
        name_label = QLabel(name)
        name_label.setObjectName("UserLabel")
        user_info_layout.addWidget(name_label)

        # Email
        email_label = QLabel(self.auth_service.current_user.Email)
        email_label.setObjectName("UserLabel")
        email_label.setStyleSheet("font-size: 12px; color: #D1E9FF;")
        user_info_layout.addWidget(email_label)

        user_layout.addWidget(user_info)
        header_layout.addWidget(user_widget)

        # Create Project button
        create_btn = QPushButton("Create Project")
        create_btn.setObjectName("PrimaryButton")
        create_btn.clicked.connect(self.show_create_dialog)
        header_layout.addWidget(create_btn)

        return header_widget

    def create_projects_table(self) -> QTableWidget:
        """Create the projects table widget"""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Index", "Project Name", "Description", "Role", "Participants"])
        table.horizontalHeader().setStretchLastSection(True)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setObjectName("ProjectsTable")
        return table

    def load_projects(self):
        """Load and display user's projects"""
        try:
            projects = projects_api.get_my_projects(self.auth_service.token)
            self.table.setRowCount(len(projects))

            for i, project in enumerate(projects):
                # Index
                self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))

                # Project Name
                self.table.setItem(i, 1, QTableWidgetItem(project.Name))

                # Description
                desc = project.Description or ""
                self.table.setItem(i, 2, QTableWidgetItem(desc))

                # Role and Participants
                try:
                    members = projects_api.get_project_members(project.Id, self.auth_service.token)
                    user_member = next((m for m in members if m.MemnerId == self.auth_service.current_user.Id), None)
                    role = user_member.Role if user_member else "Unknown"
                    participants = len(members)
                except Exception as e:
                    print(f"Error fetching members for project {project.Id}: {e}")
                    role = "Error"
                    participants = 0

                self.table.setItem(i, 3, QTableWidgetItem(role))
                self.table.setItem(i, 4, QTableWidgetItem(str(participants)))

        except Exception as e:
            print(f"Error loading projects: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load projects: {e}")

    def show_create_dialog(self):
        """Show the create project dialog"""
        dialog = CreateProjectDialog(self.auth_service)
        dialog.project_created.connect(self.on_project_created)
        dialog.exec()

    def on_project_created(self, project: ProjectDTO):
        """Handle project creation success"""
        self.load_projects()

    def handle_logout(self):
        """Handle logout button click"""
        self.logout_requested.emit()


class CreateProjectDialog(QDialog):
    """Dialog for creating a new project"""
    project_created = Signal(ProjectDTO)

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.setWindowTitle("Create Project")
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Project Name
        name_label = QLabel("Project Name *")
        self.name_input = QLineEdit()
        self.name_input.setObjectName("InputField")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        # Description
        desc_label = QLabel("Description")
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(100)
        layout.addWidget(desc_label)
        layout.addWidget(self.desc_input)

        # Deadline (placeholder, not implemented in API yet)
        deadline_label = QLabel("Deadline (optional)")
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        layout.addWidget(deadline_label)
        layout.addWidget(self.deadline_input)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        """Handle create button click"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Project name is required.")
            return

        desc = self.desc_input.toPlainText().strip()
        # Deadline not implemented in API yet

        data = ProjectCreateDTO(Name=name, Description=desc or None)

        try:
            project = projects_api.create_project(data, self.auth_service.token)
            self.project_created.emit(project)
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create project: {e}")