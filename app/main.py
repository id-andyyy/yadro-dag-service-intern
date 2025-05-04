from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

app: FastAPI = FastAPI()


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=400,
        content={"message": f"Database integrity error: {exc.orig}"}
    )


from app.routers import main_router

app.include_router(main_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
