######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Test cases for Wishlist Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from tests.factories import WishlistFactory, ProductFactory
from wsgi import app
from service.models import Wishlist, Product, db, DataValidationError

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  WISHLIST   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlist(TestCase):
    """Test Cases for Wishlist Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(Product).delete()
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_wishlist(self):
        """It should Create a Wishlist and assert that it exists"""
        fake_wishlist = WishlistFactory()
        # pylint: disable=unexpected-keyword-arg
        wishlist = Wishlist(
            name=fake_wishlist.name,
            userid=fake_wishlist.userid,
        )
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, fake_wishlist.name)
        self.assertEqual(wishlist.userid, fake_wishlist.userid)

    def test_add_a_wishlist(self):
        """It should Create an wishlist and add it to the database"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = WishlistFactory()
        wishlist.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

    @patch("service.models.db.session.commit")
    def test_add_wishlist_failed(self, exception_mock):
        """It should not create a Wishlist on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.create)

    def test_read_wishlist(self):
        """It should Read an wishlist"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Read it back
        found_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(found_wishlist.id, wishlist.id)
        self.assertEqual(found_wishlist.name, wishlist.name)
        self.assertEqual(found_wishlist.userid, wishlist.userid)
        self.assertEqual(found_wishlist.products, [])

    def test_list_all_wishlists(self):
        """It should List all Wishlists in the database"""

        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        for _ in range(5):
            wishlist = WishlistFactory()
            wishlist.create()

        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 5)
        for wishlist in wishlists:
            found_wishlist = Wishlist.find(wishlist.id)
            self.assertEqual(found_wishlist.id, wishlist.id)
            self.assertEqual(found_wishlist.name, wishlist.name)
            self.assertEqual(found_wishlist.userid, wishlist.userid)
            self.assertEqual(found_wishlist.products, wishlist.products)

    def test_find_by_name(self):
        """It should Find an Wishlist by name"""
        wishlist = WishlistFactory()
        wishlist.create()

        # Fetch it back by name
        same_wishlist = Wishlist.find_by_name(wishlist.name)[0]
        self.assertEqual(same_wishlist.id, wishlist.id)
        self.assertEqual(same_wishlist.name, wishlist.name)

    def test_serialize_an_wishlist(self):
        """It should Serialize a wishlist"""
        wishlist = WishlistFactory()
        product = ProductFactory()
        wishlist.products.append(product)
        serial_wishlist = wishlist.serialize()
        self.assertEqual(serial_wishlist["id"], wishlist.id)
        self.assertEqual(serial_wishlist["name"], wishlist.name)
        self.assertEqual(serial_wishlist["userid"], wishlist.userid)
        self.assertEqual(len(serial_wishlist["products"]), 1)
        products = serial_wishlist["products"]
        self.assertEqual(products[0]["id"], product.id)
        self.assertEqual(products[0]["wishlist_id"], product.wishlist_id)
        self.assertEqual(products[0]["name"], product.name)
        self.assertEqual(products[0]["price"], product.price)
        self.assertEqual(products[0]["description"], product.description)

    def test_deserialize_an_wishlist(self):
        """It should Deserialize an wishlist"""
        wishlist = WishlistFactory()
        wishlist.products.append(ProductFactory())
        wishlist.create()
        serial_wishlist = wishlist.serialize()
        new_wishlist = Wishlist()
        new_wishlist.deserialize(serial_wishlist)
        self.assertEqual(new_wishlist.name, wishlist.name)
        self.assertEqual(new_wishlist.userid, wishlist.userid)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an wishlist with a KeyError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an wishlist with a TypeError"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, [])

    def test_deserialize_product_key_error(self):
        """It should not Deserialize an product with a KeyError"""
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, {})

    def test_deserialize_product_type_error(self):
        """It should not Deserialize an product with a TypeError"""
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, [])

    # Todo: Update and Delete test cases
