from fastapi import FastAPI
from app.api import curriculum

app = FastAPI()
app.include_router(curriculum.router)