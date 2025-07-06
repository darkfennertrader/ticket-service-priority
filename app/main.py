from fastapi import FastAPI
from app.api.routers import tickets as tickets_router


def create_application() -> FastAPI:
    app = FastAPI(
        title="Ticket Service - async in-memory demo",
        version="0.2.0",
        description="Uses an async in-memory repo and async fake priority classifier",
    )
    app.include_router(
        tickets_router.router, prefix="/tickets", tags=["tickets"]
    )

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "message": "Ticket-service is alive. See /docs for the interactive API."
        }

    return app


app = create_application()
