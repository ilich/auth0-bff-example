from faker import Faker

from app.models.user import User


class UserService:
    def __init__(self):
        self.faker = Faker()

    def get_user_by_id(self, user_id: str) -> User:
        return User(
            id=user_id,
            username=self.faker.user_name(),
            email=self.faker.email(),
            full_name=self.faker.name(),
        )
