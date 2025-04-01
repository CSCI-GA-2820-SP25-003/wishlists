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
        wishlist = Wishlist()
        wishlist.name = fake_wishlist.name
        wishlist.userid = fake_wishlist.userid
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
        self.assertEqual(products[0]["quantity"], product.quantity)

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

    def test_delete_wishlist(self):
        """It should Delete a wishlist and its products"""
        # Create a wishlist directly through SQLAlchemy
        wishlist = Wishlist()
        wishlist.name = "Test Wishlist"
        wishlist.userid = "test_user"
        db.session.add(wishlist)
        db.session.commit()
        wishlist_id = wishlist.id

        # Create a product directly through SQLAlchemy
        product = Product()
        product.wishlist_id = wishlist_id
        product.name = "Test Product"
        product.price = 10.99
        product.description = "Test Description"
        product.quantity = 1
        db.session.add(product)
        db.session.commit()
        product_id = product.id

        # Verify the product exists
        products = (
            db.session.query(Product).filter(Product.wishlist_id == wishlist_id).all()
        )
        self.assertEqual(len(products), 1)

        # Delete the wishlist using direct SQLAlchemy
        db.session.delete(wishlist)
        db.session.commit()

        # Verify the wishlist no longer exists
        found_wishlist = db.session.get(Wishlist, wishlist_id)  # Updated method
        self.assertIsNone(found_wishlist)

        # Verify the product was also deleted
        found_product = db.session.get(Product, product_id)  # Updated method
        self.assertIsNone(found_product)

    def test_update_wishlist(self):
        """It should Update a wishlist"""
        # Create a wishlist
        wishlist = WishlistFactory()
        wishlist.create()

        # Update the wishlist
        wishlist.name = "Updated Name"
        wishlist.update()

        # Verify the update was successful
        found_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(found_wishlist.name, "Updated Name")

    def test_update_with_empty_id(self):
        """It should raise an error when updating with empty ID"""
        wishlist = Wishlist()
        wishlist.name = "Test Wishlist"
        wishlist.userid = "test_user"
        self.assertRaises(DataValidationError, wishlist.update)

    @patch("service.models.db.session.commit")
    def test_update_account_failed(self, exception_mock):
        """It should not update an Account on database error"""
        exception_mock.side_effect = Exception()
        wishlist = WishlistFactory()
        self.assertRaises(DataValidationError, wishlist.update)

    @patch("service.models.db.session.add")
    def test_create_error(self, mock_add):
        """It should handle errors on create"""
        mock_add.side_effect = Exception("Database error")
        wishlist = Wishlist()
        wishlist.name = "Test Wishlist"
        wishlist.userid = "test_user"
        self.assertRaises(DataValidationError, wishlist.create)

    def test_delete_wishlist_error_handling(self):
        """It should handle errors during wishlist deletion"""
        # Create a wishlist to delete
        wishlist = Wishlist()
        wishlist.name = "Test Delete Error"
        wishlist.userid = "test_delete_err"  # Shortened to fit within 16 chars
        wishlist.create()
        wishlist_id = wishlist.id

        # Verify the wishlist exists
        found_wishlist = Wishlist.find(wishlist_id)
        self.assertIsNotNone(found_wishlist)

        # Mock db.session.delete to raise an exception
        with patch("service.models.persistent_base.db.session.delete") as mock_delete:
            mock_delete.side_effect = Exception("Database error")
            # Attempt to delete should raise DataValidationError
            with self.assertRaises(DataValidationError):
                wishlist.delete()

    # Completed
