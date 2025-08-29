"""User repository file."""
from typing import Optional
import datetime
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures.role import Role

from ..models import User
from .abstract import Repository


class UserRepo(Repository[User]):
    """User repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository as for all users or only for one user."""
        super().__init__(type_model=User, session=session)

    async def new(
        self,
        user_id: int,
        user_name: str | None = None,
        name: str | None = None,
        age: int | None = None,
        gender: str | None = None,
        country: str | None = None,
        role: Optional[Role] = Role.USER,
    ) -> None:
        """Insert a new user into the database.

        :param user_id: Telegram user id
        :param user_name: Telegram username
        :param name: Name of User in Wanty
        :param age: Telegram profile first name
        :param gender: Telegram profile second name
        :param country: Telegram profile language code
        :param role: User's role
        """
        # Проверяем, существует ли уже пользователь
        existing_user = await self.user_register_check(active_user_id=user_id)
        if existing_user:
            # Если пользователь существует, обновляем его данные
            existing_user.user_name = user_name
            existing_user.name = name
            existing_user.age = age
            existing_user.gender = gender
            existing_user.country = country
            existing_user.role = role
            existing_user.updated_at = datetime.datetime.now(datetime.timezone.utc)
        else:
            # Если пользователь не существует, создаем нового
            new_user = User(
                user_id=user_id,
                user_name=user_name,
                name=name,
                age=age,
                gender=gender,
                country=country,
                role=role
            )
            self.session.add(new_user)
        
        await self.session.commit()

    async def get_role(self, user_id: int) -> Role:
        """Get user role by id."""
        return await self.session.scalar(
            select(User.role).where(User.user_id == int(user_id)).limit(1)
        )

    async def user_register_check(self, active_user_id: int):
        """Get user register check by id."""
        try:
            logging.info(f"Checking registration for user {active_user_id} (type: {type(active_user_id)})")
            
            # Убеждаемся, что user_id - это число
            user_id_int = int(active_user_id)
            logging.info(f"Converted user_id to int: {user_id_int}")
            
            result = await self.session.scalars(
                select(self.type_model).where(User.user_id == user_id_int).limit(1)
            )
            user = result.one_or_none()
            logging.info(f"User {active_user_id} registration check result: {user}")
            
            if user:
                logging.info(f"User found: ID={user.user_id}, Name={user.name}, Type={type(user.user_id)}")
            else:
                logging.info(f"No user found for ID {active_user_id}")
                
            return user
        except Exception as e:
            logging.error(f"Error checking registration for user {active_user_id}: {e}")
            return None

    async def get_user_by_id(self, user_id: int):
        """Get user by id."""
        statement = select(self.type_model).where(User.user_id == int(user_id))

        return (await self.session.scalars(statement)).first()

    async def get_all_user_id(self):
        """Get all user IDs."""
        statement = select(self.type_model)

        return (await self.session.scalars(statement)).all()

    async def check_database_state(self):
        """Check database state for debugging."""
        try:
            # Проверяем общее количество пользователей
            total_users = await self.session.scalar(select(self.type_model))
            logging.info(f"Total users in database: {total_users}")
            
            # Проверяем структуру таблицы
            result = await self.session.execute(select(self.type_model).limit(5))
            users = result.scalars().all()
            logging.info(f"Sample users: {[{'id': u.user_id, 'name': u.name} for u in users]}")
            
            return True
        except Exception as e:
            logging.error(f"Error checking database state: {e}")
            return False


