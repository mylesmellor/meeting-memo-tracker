from fastapi import APIRouter, HTTPException
from app.core.config import settings

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed")
async def seed_demo():
    if settings.APP_ENV == "production":
        raise HTTPException(status_code=403, detail="Not available in production")

    import subprocess
    result = subprocess.run(
        ["python", "/app/scripts/seed_demo.py"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr)
    return {"message": "Demo data seeded", "output": result.stdout}
