from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.api.routes.cases import router as cases_router
from app.api.routes.upload import router as upload_router

app = FastAPI(title="defenda.ai motor")

app.include_router(health_router, prefix="/v1")
app.include_router(cases_router, prefix="/v1")
app.include_router(upload_router, prefix="/v1")

