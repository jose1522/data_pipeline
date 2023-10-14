from fastapi import APIRouter

from db.schemas.user import UserResponse, UserInsert
from db.storage.user import UserStorage
from util.storage import get_session

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserInsert):
    session = get_session()
    storage = UserStorage(session=session)
    user = storage.upsert(user.dict())
    session.commit()
    session.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    session = get_session()
    storage = UserStorage(session=session)
    db_obj = storage.read(user_id)
    return db_obj
