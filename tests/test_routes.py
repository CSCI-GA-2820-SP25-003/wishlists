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
TestWishlist API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from decimal import Decimal
from unittest import TestCase
from wsgi import app
from service.common import status
from service.models import db, Wishlist
from .factories import WishlistFactory, ProductFactory

BASE_URL = "/wishlists"

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlistService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_wishlists(self, count):
        """Factory method to create wishlists in bulk"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.client.post(BASE_URL, json=wishlist.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Wishlist",
            )
            new_wishlist = resp.get_json()
            wishlist.id = new_wishlist["id"]
            wishlists.append(wishlist)
        return wishlists

    ######################################################################
    #  W I S H L I S T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_wishlist(self):
        """It should Read a single Wishlist"""
        # get the id of an wishlist
        wishlist = self._create_wishlists(1)[0]
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], wishlist.name)

    def test_create_wishlist(self):
        """It should Create a new Wishlist"""
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], wishlist.name, "Names does not match")
        self.assertEqual(
            new_wishlist["userid"], wishlist.userid, "Email does not match"
        )
        self.assertEqual(
            new_wishlist["products"], wishlist.products, "Product does not match"
        )

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist["name"], wishlist.name, "Names does not match")
        self.assertEqual(
            new_wishlist["userid"], wishlist.userid, "User ID does not match"
        )
        self.assertEqual(
            new_wishlist["products"], wishlist.products, "Product does not match"
        )

    def test_update_wishlist(self):
        """It should Update an existing Wishlist"""
        # create a wishlist to update
        test_wishlist = WishlistFactory()
        response = self.client.post(BASE_URL, json=test_wishlist.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the wishlist
        new_wishlist = response.get_json()
        logging.debug(new_wishlist)
        new_wishlist["name"] = "Updated Wishlist Name"
        response = self.client.put(f"{BASE_URL}/{new_wishlist['id']}", json=new_wishlist)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_wishlist = response.get_json()
        self.assertEqual(updated_wishlist["name"], "Updated Wishlist Name")

    def test_get_wishlist_list(self):
        """It should Get a list of Wishlists"""
        self._create_wishlists(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_wishlist_by_name(self):
        """It should Get a Wishlist by Name"""
        wishlists = self._create_wishlists(3)
        resp = self.client.get(BASE_URL, query_string=f"name={wishlists[1].name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], wishlists[1].name)

    def test_get_wishlist_not_found(self):
        """It should not Read a Wishlist that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, json=wishlist.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.delete(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_wishlist(self):
        """It should Delete a Wishlist"""
        # Create a wishlist to delete
        wishlist = self._create_wishlists(1)[0]

        # Add a product to the wishlist to ensure cascade delete works
        product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products",
            json=product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Delete the wishlist
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Verify the wishlist was deleted
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_wishlist(self):
        """It should Update a Wishlist"""
        # Create a wishlist to update
        test_wishlist = self._create_wishlists(1)[0]

        # Update the wishlist
        test_wishlist.name = "Updated Name"
        resp = self.client.put(
            f"{BASE_URL}/{test_wishlist.id}",
            json=test_wishlist.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Check that the update was successful
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["name"], "Updated Name")

        # Verify the update persisted
        resp = self.client.get(f"{BASE_URL}/{test_wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        retrieved_wishlist = resp.get_json()
        self.assertEqual(retrieved_wishlist["name"], "Updated Name")

    # Todo: Delete and update test cases

    ######################################################################
    #  P R O D U C T   T E S T   C A S E S
    ######################################################################

    def test_add_product(self):
        """It should Add an product to an wishlist"""
        wishlist = self._create_wishlists(1)[0]
        product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products",
            json=product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["name"], product.name)
        self.assertEqual(Decimal(str(data["price"])), product.price)
        self.assertEqual(data["description"], product.description)

        # Check that the location header was correct by getting it
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_product = resp.get_json()
        self.assertEqual(
            new_product["name"], product.name, "Product name does not match"
        )

    def test_update_product(self):
        """It should Update a product in a wishlist"""
        # create a known product
        wishlist = self._create_wishlists(1)[0]
        product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products",
            json=product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        product_id = data["id"]
        data["name"] = "XXXX"

        # send the update back
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/products/{product_id}",
            json=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/products/{product_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["id"], product_id)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["name"], "XXXX")

    def test_get_product(self):
        """It should Get an product from an wishlist"""
        # create a known product
        wishlist = self._create_wishlists(1)[0]
        product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products",
            json=product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        product_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/products/{product_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["wishlist_id"], wishlist.id)
        self.assertEqual(data["name"], product.name)
        self.assertEqual(Decimal(str(data["price"])), product.price)
        self.assertEqual(data["description"], product.description)

    def test_get_product_list(self):
        """It should Get a list of Products"""
        # add two products to wishlist
        wishlist = self._create_wishlists(1)[0]
        product_list = ProductFactory.create_batch(2)

        # Create product 1
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products", json=product_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create product 2
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products", json=product_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/products")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

    def test_delete_product(self):
        """It should Delete a product from an wishlist"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create a product for the wishlist
        product = ProductFactory()
        post_resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products",
            json=product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(post_resp.status_code, status.HTTP_201_CREATED)
        product_data = post_resp.get_json()
        product_id = product_data["id"]

        # Confirm the product exists by retrieving it
        get_resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/products/{product_id}",
            content_type="application/json",
        )
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)

        # Delete the product using the DELETE endpoint
        delete_resp = self.client.delete(
            f"{BASE_URL}/{wishlist.id}/products/{product_id}",
            content_type="application/json",
        )
        self.assertEqual(delete_resp.status_code, status.HTTP_200_OK)
        delete_data = delete_resp.get_json()
        self.assertIn("deleted", delete_data["message"].lower())

        # Verify the product no longer exists (should return 404)
        get_resp_after = self.client.get(
            f"{BASE_URL}/{wishlist.id}/products/{product_id}",
            content_type="application/json",
        )
        self.assertEqual(get_resp_after.status_code, status.HTTP_404_NOT_FOUND)

    def test_health_check(self):
        """It should return healthy status"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], 200)
        self.assertEqual(data["message"], "Healthy")

    def test_update_wishlist_not_found(self):
        """It should not update a Wishlist that is not found"""
        resp = self.client.put(
            f"{BASE_URL}/0",
            json={"name": "Not Found Wishlist", "userid": "user1"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_not_found(self):
        """It should not update a Product that is not found"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]
        # Try to update a non-existent product
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/products/0",
            json={
                "name": "Missing Product",
                "price": 13.99,
                "description": "Not Found",
            },
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wishlist_not_found(self):
        """It should not Delete a Wishlist that is not found"""
        # Try to delete a wishlist that doesn't exist
        resp = self.client.delete(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_wishlist_with_no_products(self):
        """It should Delete a Wishlist that has no products"""
        # Create a wishlist with no products
        wishlist = self._create_wishlists(1)[0]

        # Delete the wishlist
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Verify the returned message
        data = resp.get_json()
        self.assertEqual(data["message"], f"Wishlist {wishlist.id} deleted")

        # Verify the wishlist was deleted
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_bad_media_type_on_create_product(self):
        """It should not create a product with unsupported media type"""
        wishlist = self._create_wishlists(1)[0]
        product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products",
            json=product.serialize(),
            content_type="text/plain",  # Wrong media type
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_invalid_product_data(self):
        """It should not create a product with invalid data"""
        wishlist = self._create_wishlists(1)[0]
        # Missing required fields
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products",
            json={"description": "Missing required data"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_product_not_found(self):
        """It should return 404 when getting a product that doesn't exist"""
        wishlist = self._create_wishlists(1)[0]
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/products/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product_not_found(self):
        """It should return 404 when deleting a product that doesn't exist"""
        wishlist = self._create_wishlists(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}/products/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed_on_products(self):
        """It should return 405 when using an unsupported method on products collection"""
        wishlist = self._create_wishlists(1)[0]
        resp = self.client.put(f"{BASE_URL}/{wishlist.id}/products")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_products_from_nonexistent_wishlist(self):
        """It should return 404 when getting products from a non-existent wishlist"""
        resp = self.client.get(f"{BASE_URL}/0/products")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_product_for_nonexistent_wishlist(self):
        """It should return 404 when creating a product for a non-existent wishlist"""
        product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/0/products",
            json=product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_invalid_json(self):
        """It should return 400 when updating a product with invalid JSON"""
        wishlist = self._create_wishlists(1)[0]
        product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products",
            json=product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        product_id = resp.get_json()["id"]

        # Try to update with invalid data
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}/products/{product_id}",
            json={"price": "not a number"},  # Invalid price format
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_wishlist_by_nonexistent_name(self):
        """It should return empty list when querying by a name that doesn't exist"""
        resp = self.client.get(BASE_URL, query_string="name=NonExistentName")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_update_wishlist_with_missing_data(self):
        """It should not update a wishlist with missing data"""
        wishlist = self._create_wishlists(1)[0]
        # Missing userid which is required
        resp = self.client.put(
            f"{BASE_URL}/{wishlist.id}",
            json={"name": "Just a name"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_query_wishlists_by_userid(self):
        """It should Query Wishlists by userid"""
        wishlists = self._create_wishlists(3)
        # Add a different userid to the second wishlist
        test_userid = "special_user"
        wishlists[1].userid = test_userid
        wishlists[1].update()

        # Query for wishlists with that userid
        resp = self.client.get(BASE_URL, query_string=f"userid={test_userid}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["userid"], test_userid)

    def test_method_not_allowed_on_product(self):
        """It should not allow an illegal method call on a product"""
        wishlist = self._create_wishlists(1)[0]
        product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products",
            json=product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        product_id = resp.get_json()["id"]

        # Try a method that's not allowed
        resp = self.client.patch(
            f"{BASE_URL}/{wishlist.id}/products/{product_id}",
            json={"name": "Updated Name"},
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
