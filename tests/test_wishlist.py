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
from tests.factories import WishlistFactory
from wsgi import app
from service.models import Wishlist, Product, db

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
        """It should Create a Wishlist"""
        # fake_wishlist = WishlistFactory()
        # # pylint: disable=unexpected-keyword-arg
        # wishlist = Wishlist(
        #     name=fake_wishlist.name,
        #     userid=fake_wishlist.userid,
        #     email=fake_wishlist.email,
        #     phone_number=fake_wishlist.phone_number,
        #     date_joined=fake_wishlist.date_joined,
        # )
        # self.assertIsNotNone(wishlist)
        # self.assertEqual(wishlist.id, None)
        # self.assertEqual(wishlist.name, fake_wishlist.name)
        # self.assertEqual(wishlist.userid, fake_wishlist.userid)

        wishlist = WishlistFactory()
        wishlist.create()
        self.assertIsNotNone(wishlist.id)
        found = Wishlist.all()
        self.assertEqual(len(found), 1)
        data = Wishlist.find(wishlist.id)
        self.assertEqual(data.name, wishlist.name)
        self.assertEqual(data.userid, wishlist.userid)

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

    # Todo: Add your test cases here...
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
