"""
Test Factory to make fake objects for testing
"""

from factory import Factory, SubFactory, Sequence, Faker, post_generation
from service.models import Wishlist, Product


class WishlistFactory(Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Wishlist

    id = Sequence(lambda n: n)
    name = Faker("word")
    userid = Sequence(lambda n: f"User{n:04d}")

    @post_generation
    def products(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the products list"""
        if not create:
            return

        if extracted:
            self.products = extracted


class ProductFactory(Factory):
    """Creates fake Products"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """persistent class"""

        model = Product

    id = Sequence(lambda n: n)
    name = Faker("word")
    price = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    description = Faker("sentence")
    wishlist = SubFactory(WishlistFactory)
    quantity = 1
    note = None
    is_gift = False
