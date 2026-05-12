from sqlmodel import SQLModel, Field
from datetime import datetime

# Status

class Task_StatusBase(SQLModel):
    status_desc: str

class Task_Status(Task_StatusBase, table=True):
    id:          int | None = Field(default=None, primary_key=True)

class Task_StatusPublic(Task_StatusBase):
    id:          int

# Task

class TaskBase(SQLModel):
    task_title:  str
    task_desc:   str | None = None
    status_id:   int = Field(foreign_key="task_status.id")
    due:         datetime

class Task(TaskBase, table=True):
    id:          int | None = Field(default=None, primary_key=True)

class TaskPublic(TaskBase):
    id:          int

class TaskUpdate(SQLModel):
    status_id:   int