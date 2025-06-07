from fastapi import APIRouter # type: ignore

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.get("/test")
def chat_test():
    return {"message": "Chat route is working"}
