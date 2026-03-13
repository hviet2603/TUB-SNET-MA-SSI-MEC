from fastapi import APIRouter
from .app_migration.app_migration import router as app_migration_router
from .capability_delegation.capability_delegation import router as capability_delegation_router
from .car_position.car_position import router as car_position_router

router = APIRouter(prefix="/triggers", tags=["triggers"])

router.include_router(app_migration_router)
router.include_router(capability_delegation_router)
router.include_router(car_position_router)