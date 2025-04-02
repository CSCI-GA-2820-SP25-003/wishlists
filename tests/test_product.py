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
# pylint: disable=duplicate-code

"""
Test cases for Product Model
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from tests.factories import ProductFactory, WishlistFactory
from wsgi import app
from service.models import Wishlist, Product, db
from service.models import DataValidationError

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#        A D D R E S S   M O D E L   T E S T   C A S E S
######################################################################
class TestProduct(TestCase):
    """Product Model Test Cases"""

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
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_add_wishlist_product(self):
        """It should Create a Wishlist with a Product and add it to the database"""

        # Ensure the database starts empty
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        # Create a Wishlist and a Product associated with it
        wishlist = WishlistFactory()
        product = ProductFactory(wishlist=wishlist)
        wishlist.products.append(product)
        wishlist.create()  # Save the wishlist (and its products) to the database

        # Assert that the wishlist was assigned an ID and exists in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        # Retrieve the wishlist from the database and check if the product is associated
        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(new_wishlist.products), 1)
        self.assertEqual(new_wishlist.products[0].name, product.name)

        # Add another product **before** saving it to the database
        product2 = ProductFactory(wishlist=wishlist)
        wishlist.products.append(product2)
        wishlist.update()  # Recreate the wishlist to simulate saving

        # Retrieve the wishlist again and verify both products exist
        new_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(new_wishlist.products), 2)
        self.assertEqual(new_wishlist.products[1].name, product2.name)

    def test_update_wishlist_product(self):
        """It should Update a wishlist's product"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        # Create a Wishlist and a Product
        wishlist = WishlistFactory()
        product = ProductFactory(wishlist=wishlist)
        wishlist.create()  # Save the wishlist (and its products) to the database

        # Assert that the wishlist was assigned an ID and exists in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        # Fetch the wishlist from the database and get the product
        wishlist = Wishlist.find(wishlist.id)
        old_product = wishlist.products[0]

        # Assert that the description is correct
        self.assertEqual(old_product.description, product.description)

        # Update the product's description
        old_product.description = "XX"
        # Commit the change to the database
        db.session.commit()  # This saves the change
        # Fetch the product back and check the updated description
        updated_product = Product.find(old_product.id)
        self.assertEqual(updated_product.description, "XX")

    def test_update_product_quantity(self):
        """It should Update a wishlist product's quantity"""
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])

        # Create a Wishlist and a Product
        wishlist = WishlistFactory()
        product = ProductFactory(wishlist=wishlist)
        wishlist.create()  # Save the wishlist (and its products) to the database

        # Assert that the wishlist was assigned an ID and exists in the database
        self.assertIsNotNone(wishlist.id)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

        # Fetch the wishlist from the database and get the product
        wishlist = Wishlist.find(wishlist.id)
        old_product = wishlist.products[0]

        # Assert that the description is correct
        self.assertEqual(old_product.description, product.description)

        # Update the product's description
        old_product.quantity = 2
        # Commit the change to the database
        db.session.commit()  # This saves the change
        # Fetch the product back and check the updated description
        updated_product = Product.find(old_product.id)
        self.assertEqual(updated_product.quantity, 2)

    def test_serialize_an_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        serial_product = product.serialize()
        self.assertEqual(serial_product["id"], product.id)
        self.assertEqual(serial_product["wishlist_id"], product.wishlist_id)
        self.assertEqual(serial_product["name"], product.name)
        self.assertEqual(serial_product["price"], product.price)
        self.assertEqual(serial_product["description"], product.description)
        self.assertEqual(serial_product["quantity"], product.quantity)

    def test_deserialize_an_product(self):
        """It should deserialize a Product"""
        product = ProductFactory()
        product.create()
        new_product = Product()
        new_product.deserialize(product.serialize())
        self.assertEqual(new_product.wishlist_id, product.wishlist_id)
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.price, product.price)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(new_product.quantity, product.quantity)

    # Completed

    def test_delete_product(self):
        """It should delete a product from a wishlist"""
        # Create a Wishlist and add two products
        wishlist = WishlistFactory()
        product1 = ProductFactory(wishlist=wishlist)
        product2 = ProductFactory(wishlist=wishlist)
        wishlist.products.append(product1)
        wishlist.products.append(product2)
        wishlist.create()  # Save the wishlist and its products to the database

        # Retrieve the wishlist from the database and verify both products exist
        wishlist_db = Wishlist.find(wishlist.id)
        self.assertEqual(len(wishlist_db.products), 2)

        # Delete the first product from the database
        product1.delete()

        # Retrieve the wishlist again to confirm the product has been deleted
        updated_wishlist = Wishlist.find(wishlist.id)
        self.assertEqual(len(updated_wishlist.products), 1)
        self.assertEqual(updated_wishlist.products[0].id, product2.id)

    def test_delete_product_error_handling(self):
        """It should handle errors during product deletion"""
        # Create a Wishlist and a product
        wishlist = WishlistFactory()
        product = ProductFactory(wishlist=wishlist)
        wishlist.products.append(product)
        wishlist.create()

        # Verify the product exists
        wishlist_db = Wishlist.find(wishlist.id)
        self.assertEqual(len(wishlist_db.products), 1)
        product_id = wishlist_db.products[0].id

        # Mock db.session.commit to raise an exception
        with patch("service.models.persistent_base.db.session.commit") as mock_commit:
            mock_commit.side_effect = Exception("Database error")
            # Attempt to delete should raise DataValidationError
            with self.assertRaises(DataValidationError):
                product.delete()

        # Verify the product still exists (delete failed)
        product_exists = db.session.get(Product, product_id)
        self.assertIsNotNone(product_exists)



