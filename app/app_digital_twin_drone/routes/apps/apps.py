from fastapi import APIRouter
from .app_migration.app_migration import router as app_migration_router

router = APIRouter(prefix="/apps", tags=["apps"])

router.include_router(app_migration_router)