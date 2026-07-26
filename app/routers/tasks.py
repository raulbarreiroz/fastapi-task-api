from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
from datetime import datetime, timezone
import uuid

from app.schemas.task import TaskCreate, TaskResponse
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])
UserId = Annotated[str, Depends(get_current_user)]

# In memory database
fake_db = {}

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task_data: TaskCreate, _: UserId):
    # BUSINESS RULE: If the title contains "URGENTE" (uppercase or lowercase),
    # ie force completed=False to make the user see it as pending.
    completed_final = task_data.completed
    if "URGENTE" in task_data.title.upper():
        completed_final = False

    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    new_task = {
        "id": task_id,
        "title": task_data.title,
        "description": task_data.description,
        "completed": completed_final,
        "created_at": now,
        "updated_at": now,
    }

    fake_db[task_id] = new_task

    return new_task

@router.get("/", response_model=List[TaskResponse])
async def list_tasks(_: UserId):
    return list(fake_db.values())

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, _: UserId):
    task = fake_db.get(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.delete("/", response_model=List[TaskResponse])
async def delete_all_tasks(_: UserId):
    deleted_tasks = list(fake_db.values())
    fake_db.clear()
    return deleted_tasks