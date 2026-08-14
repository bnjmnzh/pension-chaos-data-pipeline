from fastapi import FastAPI

from app.config import Settings
from app.api.v1.endpoints import router as member_router

app = FastAPI(
    title=Settings.PROJECT_NAME,
    description=Settings.DESCRIPTION
)

app.include_router(member_router, prefix=Settings.API_V1_STR, tags=["Member Data Generation"])

@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}