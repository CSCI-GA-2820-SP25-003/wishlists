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
Wishlist Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Wishlist
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Wishlist, Product
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
# CREATE A NEW WISHLIST
######################################################################
@app.route("/wishlists", methods=["POST"])
def create_wishlists():
    """
    Creates a Wishlist
    This endpoint will create a Wishlist based the data in the body that is posted
    """
    app.logger.info("Request to create a Wishlist")
    check_content_type("application/json")

    # Create the wishlist
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.create()

    # Create a message to return
    message = wishlist.serialize()
    # Todo: Uncomment this code when get_wishlists is implemented
    location_url = url_for("get_wishlists", wishlist_id=wishlist.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# RETRIEVE AN ACCOUNT
######################################################################


@app.route("/wishlists/<int:wishlist_id>", methods=["GET"])
def get_wishlists(wishlist_id):
    """
    Retrieve a single Wishlist

    This endpoint will return an Wishlist based on it's id
    """
    app.logger.info("Request for Wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    return jsonify(wishlist.serialize()), status.HTTP_200_OK

######################################################################
# LIST ALL WISHLISTS
######################################################################


@app.route("/wishlists", methods=["GET"])
def list_wishlists():
    """Returns all of the Wishlists"""
    app.logger.info("Request for wishlist list")

    wishlists = []

    category = request.args.get("category")
    name = request.args.get("name")
    available = request.args.get("available")
    gender = request.args.get("gender")

    if category:
        app.logger.info("Find by category: %s", category)
        wishlists = Wishlist.find_by_category(category)
    elif name:
        app.logger.info("Find by name: %s", name)
        wishlists = Wishlist.find_by_name(name)
    elif available:
        app.logger.info("Find by available: %s", available)
        available_value = available.lower() in ["true", "yes", "1"]
        wishlists = Wishlist.find_by_availability(available_value)
    elif gender:
        app.logger.info("Find by gender: %s", gender)
        wishlists = Wishlist.find_by_gender(gender.upper())  
    else:
        app.logger.info("Find all")
        wishlists = Wishlist.all()

    results = [wishlist.serialize() for wishlist in wishlists]
    app.logger.info("Returning %d wishlists", len(results))
    return jsonify(results), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                P R O D U C T  M E T H O D S
# ---------------------------------------------------------------------

######################################################################
# ADD A PRODUCT TO A WISHLIST
######################################################################


@app.route("/wishlists/<int:wishlist_id>/products", methods=["POST"])
def create_products(wishlist_id):
    """
    Create an Product on a Wishlist

    This endpoint will add a product to a wishlist
    """
    app.logger.info("Request to create a Product for Wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Create a product from the json data
    product = Product()
    product.deserialize(request.get_json())

    # Append the product to the wishlist
    wishlist.products.append(product)
    wishlist.update()

    # Prepare a message to return
    message = product.serialize()

    # Todo: Uncomment this code when get_products is implemented
    # Send the location to GET the new item
    # location_url = url_for(
    #     "get_products",
    #     wishlist_id=wishlist.id,
    #     product_id=product.id,
    #     _external=True
    # )
    location_url = "/"
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# UPDATE A PRODUCT
######################################################################


@app.route("/wishlists/<int:wishlist_id>/products/<int:product_id>", methods=["PUT"])
def update_products(wishlist_id, product_id):
    """
    Update a Product

    This endpoint will update a Product based the body that is posted
    """
    app.logger.info(
        "Request to update Product %s for Wishlist id: %s", (product_id, wishlist_id)
    )
    check_content_type("application/json")

    # See if the product exists and abort if it doesn't
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{product_id}' could not be found.",
        )

    # Update from the json in the body of the request
    product.deserialize(request.get_json())
    product.id = product_id
    product.update()

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, f"Content-Type must be {content_type}"
    )
