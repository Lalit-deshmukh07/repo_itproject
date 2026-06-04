from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from.controllers.task_controller import router as task_router
from.database import engine
from.models import Base

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(task_router)

@app.get("/")
def read_root():
    return {"message": "Task API running"}