from fastapi import FastAPI, HTTPException, Query
from typing import Annotated
from sqlmodel import select

from models import *
from database import SessionDep, create_db_and_tables


app = FastAPI()
@app.on_event('startup')
def on_startup():
    create_db_and_tables()


#
# Create status (POST)
#

@app.post("/statuses/", response_model=Task_StatusPublic)
def create_status(status: Task_StatusBase, session: SessionDep):

    db_status = Task_Status.model_validate(status)
    session.add(db_status)
    session.commit()
    session.refresh(db_status)
    return db_status

#
# Get all statuses (GET)
#

@app.get("/statuses/", response_model=list[Task_StatusPublic])
def get_all_statuses(
        session: SessionDep, 
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100
):
    statuses = session.exec(select(Task_Status).offset(offset).limit(limit)).all()
    return statuses

#
# Update status (PATCH)
#

@app.patch("/statuses/{status_id}", response_model=Task_StatusPublic)
def update_status(status_id: int, status: Task_StatusBase, session: SessionDep):

    status_db = session.get(Task_Status, status_id)
    if not status_db:
        raise HTTPException(status_code=404, detail=f"Status with id {status_id} not found")
    status_data = status.model_dump(exclude_unset=True)
    status_db.sqlmodel_update(status_data)
    
    session.add(status_db)
    session.commit()
    session.refresh(status_db)
    return status_db

#
# Delete status (DELETE)
#

@app.delete("/statuses/{status_id}")
def delete_status(status_id: int, session: SessionDep):

    task_status = session.get(Task_Status, status_id)
    if not task_status:
        raise HTTPException(status_code=404, detail=f"Status with id {status_id} not found")
    session.delete(task_status)
    session.commit()
    return {"ok", True}

#
# Create task (POST)
#

@app.post("/tasks/", response_model=TaskPublic)
def create_task(task: TaskBase, session: SessionDep):

    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

#
# Get task by id (GET)
#

@app.get("/tasks/{task_id}", response_model=TaskPublic)
def get_task_by_id(task_id: int, session: SessionDep):

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task

#
# Get all tasks (GET)
#

@app.get("/", response_model=list[TaskPublic])
def get_all_tasks(
        session: SessionDep, 
        offset: int = 0,
        limit: Annotated[int, Query(le=100)] = 100
):
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks

#
# Update task status (PATCH)
#

@app.patch("/tasks/{task_id}", response_model=TaskPublic)
def update_task_status(task_id: int, task: TaskUpdate, session: SessionDep):

    task_db = session.get(Task, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    task_data = task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)
    
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db

#
# Delete a task (DELETE)
#

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep):

    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    session.delete(task)
    session.commit()
    return {"ok", True}