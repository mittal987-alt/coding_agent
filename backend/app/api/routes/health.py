#
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.api.dependencies import HealthManagerDep

router = APIRouter()
@router.get(
    "/",
    summary="Application health",
)
async def health(
    health_manager: HealthManagerDep,
):

    report = await health_manager.health()

    return {
        "success": True,
        "data": report,
    }
@router.get(
    "/live",
    summary="Liveness probe",
)
async def live():

    return {
        "status": "alive",
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }
@router.get(
    "/ready",
    summary="Readiness probe",
)
async def ready(
    health_manager: HealthManagerDep,
):

    ready = await health_manager.ready()

    return {
        "ready": ready,
    }
@router.get(
    "/version",
)
async def version(
    health_manager: HealthManagerDep,
):

    return {
        "version": health_manager.version,
        "environment": health_manager.environment,
    }
@router.get(
    "/services",
)
async def services(
    health_manager: HealthManagerDep,
):

    return {
        "services": await health_manager.services(),
    }
@router.get(
    "/metrics",
)
async def metrics(
    health_manager: HealthManagerDep,
):

    return await health_manager.metrics()