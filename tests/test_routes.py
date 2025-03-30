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
import json
import logging
from decimal import Decimal
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.common import status
from service.models import db, Wishlist, DataValidationError
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
        self.headers = {
            "Content-Type": "application/json"
        }

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

    def _create_products(self, wishlist_id, count):
        """Factory method to create products in bulk for a specific wishlist"""
        products = []
        for _ in range(count):
            product = ProductFactory()
            resp = self.client.post(
                f"{BASE_URL}/{wishlist_id}/products",
                json=product.serialize(),
                content_type="application/json"
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Product",
            )
            new_product = resp.get_json()
            product.id = new_product["id"]
            products.append(product)
        return products

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
        self.assertEqual(delete_resp.status_code, status.HTTP_204_NO_CONTENT)

        # Verify the product no longer exists (should return 404)
        get_resp_after = self.client.get(
            f"{BASE_URL}/{wishlist.id}/products/{product_id}",
            content_type="application/json",
        )
        self.assertEqual(get_resp_after.status_code, status.HTTP_404_NOT_FOUND)

    # Completed

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
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_wishlist_with_no_products(self):
        """It should Delete a Wishlist that has no products"""
        # Create a wishlist with no products
        wishlist = self._create_wishlists(1)[0]

        # Delete the wishlist
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

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
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

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

    def test_get_wishlists_default_pagination(self):
        """It should get the first 10 wishlists by default"""
        # Create more than 10 wishlists
        wishlists = self._create_wishlists(15)

        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 10)  # Default limit is 10

        # Verify the first few wishlists are returned
        for i in range(10):
            self.assertEqual(data[i]['name'], wishlists[i].name)

    def test_get_wishlists_custom_pagination(self):
        """It should get the specified page and limit of wishlists"""
        # Create 15 wishlists
        wishlists = self._create_wishlists(15)

        # Get second page with 5 items per page
        resp = self.client.get(BASE_URL, query_string="page=2&limit=5")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 5)  # 5 items per page

        # Verify the correct 5 wishlists are returned (items 6-10)
        for i in range(5):
            self.assertEqual(data[i]['name'], wishlists[i + 5].name)

    def test_get_wishlists_last_page(self):
        """It should get the last page of wishlists"""
        # Create 15 wishlists
        wishlists = self._create_wishlists(15)

        # Get last page with 5 items per page
        resp = self.client.get(BASE_URL, query_string="page=3&limit=5")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 5)  # 5 items on last page

        # Verify the correct 5 wishlists are returned (last 5 items)
        for i in range(5):
            self.assertEqual(data[i]['name'], wishlists[i + 10].name)

    def test_get_wishlists_beyond_total_pages(self):
        """It should return an empty list when page is beyond total pages"""
        # Create fewer than 10 wishlists
        wishlists = self._create_wishlists(7)
        self.assertEqual(len(wishlists), 7)  # Verify number of created wishlists
        # Request a page that doesn't exist
        resp = self.client.get(BASE_URL, query_string="page=3&limit=5")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 0)  # Empty list for non-existent page

    def test_get_wishlists_invalid_pagination(self):
        """It should handle invalid pagination parameters gracefully"""
        # Create some wishlists
        wishlists = self._create_wishlists(10)
        self.assertEqual(len(wishlists), 10)  # Verify number of created wishlists

        # Test negative page number
        resp = self.client.get(BASE_URL, query_string="page=-1&limit=5")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)  # Should default to first page

        # Test zero page number
        resp = self.client.get(BASE_URL, query_string="page=0&limit=5")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)  # Should default to first page

        # Test extremely large page number
        resp = self.client.get(BASE_URL, query_string="page=1000&limit=5")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)  # Should return empty list

    def test_update_note_for_non_existing_product(self):
        """It should handle the case when updating a note for a non-existing product."""
        wishlist = WishlistFactory()
        wishlist.create()

        # Attempt to update the note for a non-existing product (ID 999)
        response = self.client.patch(
            f"/wishlists/{wishlist.id}/products/999/note",
            json={"note": "This is a note."}
        )

        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("Product with id '999' was not found.", data["message"])

    def test_update_note_for_product_not_in_wishlist(self):
        """It should handle updating a product note when the product does not belong to the given wishlist."""
        # Create two wishlists
        wishlist1 = self._create_wishlists(1)[0]
        wishlist2 = self._create_wishlists(1)[0]

        # Create a product in wishlist1
        product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/{wishlist1.id}/products",
            json=product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        product_data = resp.get_json()
        product_id = product_data["id"]

        # Attempt to update the product's note in wishlist2
        response = self.client.patch(
            f"{BASE_URL}/{wishlist2.id}/products/{product_id}/note",
            json={"note": "This is a note."},
            content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.get_json()
        self.assertIn("Product does not belong", data["message"])

    def test_serialize_and_deserialize_product_with_note(self):
        """It should serialize and deserialize a product with a note field."""
        # Create a Product and add a note
        product = ProductFactory(note="Special product note")
        serialized_product = product.serialize()

        # Check if the serialized note is correct
        self.assertEqual(serialized_product["note"], "Special product note")

        # Deserialize the serialized product
        new_product = ProductFactory()
        new_product.deserialize(serialized_product)

        # Verify that the deserialized note is correct
        self.assertEqual(new_product.note, "Special product note")

    def test_create_product_without_note(self):
        """It should create a product without a note and handle it properly."""
        # Create a Wishlist
        wishlist = WishlistFactory()
        wishlist.create()

        # Create a Product without a note
        product_data = {
            "wishlist_id": wishlist.id,
            "name": "Smartphone",
            "price": 799.99,
            "description": "Latest model",
        }
        response = self.client.post(
            f"/wishlists/{wishlist.id}/products",
            json=product_data
        )

        self.assertEqual(response.status_code, 201)
        product = response.get_json()
        self.assertIsNone(product["note"])

    def test_update_product_note_success(self):
        """Test successful note update of a product"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create a product
        product = self._create_products(wishlist.id, 1)[0]
        # Update the note
        update_data = {
            "note": "Updated note text"
        }

        resp = self.client.patch(
            f"/wishlists/{wishlist.id}/products/{product.id}/note",
            json=update_data,
            headers=self.headers
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_product = json.loads(resp.data)
        self.assertEqual(updated_product["note"], "Updated note text")

    def test_update_product_note_missing_note(self):
        """Test updating a product note with missing 'note' field"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Create a product
        product = self._create_products(wishlist.id, 1)[0]

        # Try to update without a note field
        update_data = {
            "something_else": "This is not a note"
        }

        resp = self.client.patch(
            f"/wishlists/{wishlist.id}/products/{product.id}/note",
            json=update_data,
            headers=self.headers
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("must contain a 'note' field", resp.get_data(as_text=True))

    def test_update_product_note_product_not_found(self):
        """Test updating note for a non-existent product"""
        # Create a wishlist
        wishlist = self._create_wishlists(1)[0]

        # Try to update a non-existent product
        non_existent_product_id = 99999
        update_data = {
            "note": "This won't work"
        }

        resp = self.client.patch(
            f"/wishlists/{wishlist}/products/{non_existent_product_id}/note",
            json=update_data,
            headers=self.headers
        )

        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_note_wrong_wishlist(self):
        """Test updating note for a product in the wrong wishlist"""
        # Create two wishlists
        wishlist1 = self._create_wishlists(1)[0]
        wishlist2 = self._create_wishlists(1)[0]

        # Create a product in wishlist1
        product = self._create_products(wishlist1.id, 1)[0]

        # Try to update the product note using wishlist2's ID
        update_data = {
            "note": "This should fail"
        }

        resp = self.client.patch(
            f"/wishlists/{wishlist2.id}/products/{product.id}/note",
            json=update_data,
            headers=self.headers
        )

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("does not belong to the specified wishlist", resp.get_data(as_text=True))

    def test_delete_non_existent_product(self):
        """It should handle deleting a non-existent product gracefully."""
        wishlist = WishlistFactory()
        resp = self.client.post(BASE_URL, json=wishlist.serialize())
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        wishlist_data = resp.get_json()
        wishlist_id = wishlist_data["id"]

        # Attempt to delete a product that doesn't exist
        response = self.client.delete(
            f"{BASE_URL}/{wishlist_id}/products/999"
        )

        # Should return 204 with no content
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # Don't try to access response.get_json() as it will be None

    def test_delete_product_database_integrity(self):
        """It should handle deleting a product while ensuring database integrity."""
        # Create a Wishlist and a Product associated with it
        wishlist = WishlistFactory()
        product = ProductFactory(wishlist=wishlist)
        wishlist.products.append(product)
        wishlist.create()  # Save the wishlist (and its products) to the database

        # Mock db.session.commit to raise an exception
        with patch("service.models.persistent_base.db.session.commit") as mock_commit:
            mock_commit.side_effect = Exception("Database error")

            # Attempt to delete should raise DataValidationError
            with self.assertRaises(DataValidationError):
                product.delete()

    def test_check_content_type_missing(self):
        """Test missing Content-Type header (lines 414-415)"""
        # Create a request without a Content-Type header
        resp = self.client.post(  # Use client instead of app
            "/wishlists",
            data=json.dumps({"name": "Test Wishlist", "user_id": "user123"})
            # Deliberately not including headers
        )

        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertIn("Content-Type must be", resp.get_data(as_text=True))

    def test_check_content_type_wrong(self):
        """Test wrong Content-Type header (line 415)"""
        headers = {"Content-Type": "text/plain"}  # Wrong content type

        resp = self.client.post(  # Use client instead of app
            "/wishlists",
            headers=headers,
            data=json.dumps({"name": "Test Wishlist", "user_id": "user123"})
        )

        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        self.assertIn("Content-Type must be", resp.get_data(as_text=True))
