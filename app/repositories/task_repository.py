from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, TaskStatus


class TaskRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def get_all_by_owner(self, owner_id: int) -> list[Task]:
        result = await self.db.execute(select(Task).where(Task.owner_id == owner_id))
        return list(result.scalars().all())

    async def create(
        self,
        title: str,
        description: Optional[str],
        status: TaskStatus,
        owner_id: int,
    ) -> Task:
        task = Task(title=title, description=description, status=status, owner_id=owner_id)
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(self, task: Task, updates: dict) -> Task:
        for key, value in updates.items():
            setattr(task, key, value)
        task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.db.delete(task)
        await self.db.commit()
