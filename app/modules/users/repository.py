import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return self._db.execute(stmt).scalar_one_or_none()

    def create(self, user: User) -> User:
        self._db.add(user)
        self._db.flush()
        return user

    def update(self, user: User) -> User:
        self._db.flush()
        return user

    def get_all(self, offset: int = 0, limit: int = 20) -> tuple[list[User], int]:
        from sqlalchemy import func
        count_stmt = select(func.count()).select_from(User)
        total = self._db.execute(count_stmt).scalar_one()
        stmt = select(User).offset(offset).limit(limit).order_by(User.created_at.desc())
        items = list(self._db.execute(stmt).scalars().all())
        return items, total
