import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from datetime import datetime

from main import app
from database import get_session
from models import Task_Status, Task


#
# Create fixtures 
#


@pytest.fixture(name="session")  
def session_fixture():

    # use sqllite for testing
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")  
def client_fixture(session: Session):

    def get_session_override():  
        return session

    app.dependency_overrides[get_session] = get_session_override  

    client = TestClient(app)  
    yield client  
    app.dependency_overrides.clear() 


#
# Endpoint tests - Task Status
#


def test_create_status(client: TestClient):

    response = client.post(
        "/statuses/",
        json={"status_desc": "Active"}
    )
    data = response.json()
    
    assert response.status_code == 200
    assert data["status_desc"] == "Active"


def test_get_all_statuses(session: Session, client: TestClient):

    task_status_1 = Task_Status(status_desc="Active")
    task_status_2 = Task_Status(status_desc="Complete")
    session.add(task_status_1)
    session.add(task_status_2)
    session.commit()

    response = client.get("/statuses/")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 2
    assert data[0]["status_desc"] == "Active"
    assert data[1]["status_desc"] == "Complete"


def test_update_status_description_invalid_id(session: Session, client: TestClient):

    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()

    response = client.patch(
        f"/statuses/{task_status.id + 1}",
        json={"status_desc": "In Progress"}
    )

    assert response.status_code == 404


def test_update_status_description(session: Session, client: TestClient):

    status = Task_Status(status_desc="Active")
    session.add(status)
    session.commit()

    response = client.patch(
        f"/statuses/{status.id}",
        json={"status_desc": "In Progress"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["status_desc"] == "In Progress"
    

def test_delete_status_id_does_not_exist(session: Session, client: TestClient):

    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()

    response = client.delete(f"/statuses/{task_status.id + 1}")

    assert response.status_code == 404


def test_delete_status_id_exists(session: Session, client: TestClient):

    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()

    response = client.delete(f"/statuses/{task_status.id}")
    data = response.json()

    assert response.status_code == 200
    assert "ok" in data


#
# Endpoint tests - Task
#


def test_create_task(session: Session, client: TestClient):

    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()

    response = client.post(
        "/tasks/",
        json={
            "task_title": "A task title",
            "task_desc": "A task description",
            "status_id": str(task_status.id),
            "due": "2026-05-11 19:20:41"
        }
    )
    
    assert response.status_code == 200


def test_create_task_no_description(session: Session, client: TestClient):

    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()

    response = client.post(
        "/tasks/",
        json={
            "task_title": "A task title",
            "status_id": str(task_status.id),
            "due": "2026-05-11 19:20:41"
        }
    )
    
    assert response.status_code == 200


def test_get_task_by_id_invalid_id(session: Session, client: TestClient):
    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()
    
    task = Task(task_title="A task title",
                status_id=task_status.id, 
                due=datetime(2026, 5, 11, 19, 20))
    session.add(task)
    session.commit()

    response = client.get(f"/tasks/{task.id + 1}")

    assert response.status_code == 404


def test_get_task_by_id(session: Session, client: TestClient):
    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()
    
    task = Task(task_title="A task title",
                status_id=task_status.id, 
                due=datetime(2026, 5, 11, 19, 20))
    session.add(task)
    session.commit()

    response = client.get(f"/tasks/{task.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["task_title"] == "A task title"
    assert data["status_id"] == task_status.id
    assert data["due"] == "2026-05-11T19:20:00"


def test_get_all_tasks(session: Session, client: TestClient):
    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()
    
    task_1 = Task(task_title="A task title",
                  status_id=task_status.id, 
                  due=datetime(2026, 5, 11, 19, 20))
    task_2 = Task(task_title="A task title 2",
                  status_id=task_status.id, 
                  due=datetime(2026, 5, 11, 20, 20))
    session.add(task_1)
    session.add(task_2)
    session.commit()

    response = client.get("/")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["task_title"] == "A task title"
    assert data[0]["status_id"] == task_status.id
    assert data[0]["due"] == "2026-05-11T19:20:00"
    assert data[1]["task_title"] == "A task title 2"
    assert data[1]["status_id"] == task_status.id
    assert data[1]["due"] == "2026-05-11T20:20:00"


def test_update_task_status_invalid_id(session: Session, client: TestClient):
    task_status_1 = Task_Status(status_desc="Active")
    task_status_2 = Task_Status(status_desc="In progress")
    session.add(task_status_1)
    session.add(task_status_2)
    session.commit()
    
    task = Task(task_title="A task title",
                status_id=task_status_1.id, 
                due=datetime(2026, 5, 11, 19, 20))
    session.add(task)
    session.commit()

    # initially set to task_status_1
    response = client.get(f"/tasks/{task.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["status_id"] == task_status_1.id

    # update fails as invalid task id passed
    response = client.patch(
        f"/tasks/{task.id + 1}",
        json={"status_id": task_status_2.id}
    )
    assert response.status_code == 404

    # task status still set to task_status_1
    response = client.get(f"/tasks/{task.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["status_id"] == task_status_1.id


def test_update_task_status(session: Session, client: TestClient):
    task_status_1 = Task_Status(status_desc="Active")
    task_status_2 = Task_Status(status_desc="In progress")
    session.add(task_status_1)
    session.add(task_status_2)
    session.commit()
    
    task = Task(task_title="A task title",
                status_id=task_status_1.id, 
                due=datetime(2026, 5, 11, 19, 20))
    session.add(task)
    session.commit()

    # initially set to task_status_1
    response = client.get(f"/tasks/{task.id}")
    data = response.json()
    assert response.status_code == 200
    assert data["status_id"] == task_status_1.id

    response = client.patch(
        f"/tasks/{task.id}",
        json={"status_id": task_status_2.id}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["task"]["status_id"] == task_status_2.id


def test_delete_task_invalid_id(session: Session, client: TestClient):
    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()
    
    task = Task(task_title="A task title",
                status_id=task_status.id, 
                due=datetime(2026, 5, 11, 19, 20))
    session.add(task)
    session.commit()

    response = client.delete(f"/tasks/{task.id + 1}")

    assert response.status_code == 404


def test_delete_task(session: Session, client: TestClient):
    task_status = Task_Status(status_desc="Active")
    session.add(task_status)
    session.commit()
    
    task = Task(task_title="A task title",
                status_id=task_status.id, 
                due=datetime(2026, 5, 11, 19, 20))
    session.add(task)
    session.commit()

    response = client.delete(f"/tasks/{task.id}")

    assert response.status_code == 200