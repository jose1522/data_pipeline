from fastapi import APIRouter, Header
from pydantic import conlist

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


@router.post("/bulk", status_code=201)
async def create_users(users: conlist(UserInsert, min_items=1, max_items=1000)):
    session = get_session()
    storage = UserStorage(session=session)
    storage.bulk_upsert([user.dict() for user in users])
    session.commit()


@router.get("/", response_model=list[UserResponse])
async def get_users(limit: int = 100, offset: int = 0):
    session = get_session()
    storage = UserStorage(session=session)
    db_obj = storage.all(skip=offset, limit=limit)
    return db_obj


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    session = get_session()
    storage = UserStorage(session=session)
    db_obj = storage.read(user_id)
    return db_obj


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    x_soft_delete: bool = Header(default=True),
):
    session = get_session()
    storage = UserStorage(session=session)
    storage.delete(user_id, soft_delete=x_soft_delete)
    session.commit()


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserInsert):
    session = get_session()
    storage = UserStorage(session=session)
    db_obj = storage.update(user_id, user.dict())
    session.commit()
    session.refresh(db_obj)
    return db_obj
