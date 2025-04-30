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
Product Steps

Steps file for Product.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the following products")
def step_impl(context):
    """Delete all Products and load new ones"""

    # Get a list all of the products
    wishlist_id = context.wishlist_ids[0]
    # print("All wishlist IDs:", context.wishlist_ids)
    # print("Posting to wishlist:", wishlist_id)
    rest_endpoint = f"{context.base_url}/wishlists/{wishlist_id}/products"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)
    # and delete them one by one
    for product in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{product['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new products
    for row in context.table:
        payload = {
            "name": row["name"],
            "wishlist_id": wishlist_id,
            "price": float(row["price"]),  # for Decimal(10,2), float is acceptable
            # "min_price": int(row["min_price"]),  # if your schema uses this — remove if not
            # "max_price": int(row["max_price"]),  # same here
            "quantity": int(row["quantity"]),
            "description": row["description"],
            "note": row["note"],
            "is_gift": row["is_gift"].lower() == "true",
            "purchased": row["purchased"].lower() == "true",
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        # print("Response Body:", context.resp.text)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
