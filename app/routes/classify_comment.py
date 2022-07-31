from fastapi import APIRouter
from ..machine_learning import data_loader, get_predictions, pd

router = APIRouter()

@router.post("/")
async def classify():
    pass