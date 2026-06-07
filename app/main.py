import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import auth, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Task Manager API", version="1.0.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
