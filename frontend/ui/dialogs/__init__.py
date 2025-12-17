"""
Диалоговые окна для работы внутри проекта:
- создание задачи
- создание группы задач
- добавление участника
- просмотр участников проекта
"""

from .new_task_dialog import NewTaskDialog
from .new_group_dialog import NewTaskGroupDialog
from .add_member_dialog import AddMemberDialog
from .members_list_dialog import MembersListDialog

__all__ = [
    "NewTaskDialog",
    "NewTaskGroupDialog",
    "AddMemberDialog",
    "MembersListDialog",
]



