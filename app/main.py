from fastapi import FastAPI
from app.routers import main_router

app: FastAPI = FastAPI()
app.include_router(main_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
