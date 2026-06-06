from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, User
from app.repositories.task_repository import TaskRepository
from app.schemas import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.task_repo = TaskRepository(db)

    async def get_all(self, current_user: User) -> list[Task]:
        return await self.task_repo.get_all_by_owner(current_user.id)

    async def get_one(self, task_id: int, current_user: User) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None or task.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    async def create(self, task_data: TaskCreate, current_user: User) -> Task:
        return await self.task_repo.create(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            owner_id=current_user.id,
        )

    async def update(self, task_id: int, task_data: TaskUpdate, current_user: User) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None or task.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        updates = task_data.model_dump(exclude_unset=True)
        return await self.task_repo.update(task, updates)

    async def delete(self, task_id: int, current_user: User) -> None:
        task = await self.task_repo.get_by_id(task_id)
        if task is None or task.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        await self.task_repo.delete(task)
