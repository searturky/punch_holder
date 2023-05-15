from app.api.v1 import router as v1
from fastapi import APIRouter

router = APIRouter()
router.include_router(v1.router, prefix="/v1")


@router.post("/actuator/health")
async def health():
    # template = env.get_template("item.html")
    # res = templates.TemplateResponse("item.html", {"request": "312", "user": "123"})
    # r = template.render(user="123")
    # print(r)

    return {"status": "OK"}
