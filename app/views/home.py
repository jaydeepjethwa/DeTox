from fastapi import APIRouter, Request
from settings import templates

router = APIRouter()

@router.get("/", tags=["Home Page"])
def landing(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})