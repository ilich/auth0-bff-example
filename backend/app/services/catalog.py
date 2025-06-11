import faker

from app.models.catalog import Product


class CatalogService:
    def __init__(self):
        self.faker = faker.Faker()

    def get_catalog(self, count: int = 10) -> list:
        """Generate a list of fake catalog items."""
        return [
            Product(
                id=i + 1,
                name=self.faker.name(),
                description=self.faker.text(),
                price=self.faker.pydecimal(left_digits=3, right_digits=2, positive=True),
                stock=self.faker.random_int(min=0, max=100),
            )
            for i in range(count)
        ]
