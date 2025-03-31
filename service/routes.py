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
# GET HEALTH CHECK
######################################################################
@app.route("/health")
def health_check():
    """Let them know our heart is still beating"""
    return jsonify(status=200, message="Healthy"), status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Wishlist REST API Service",
            version="1.0",
            paths=url_for("list_wishlists", _external=True),
        ),
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
    # Completed
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
    """
    Returns paginated Wishlists with optional name filtering

    Query Parameters:
    - name: Filter wishlists by name
    - page: Page number for pagination (default: 1)
    - limit: Number of items per page (default: 10)
    """
    app.logger.info("Request for Wishlists list")

    # Extract filter and pagination parameters
    name = request.args.get("name")
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    # Validate and normalize page and limit
    page = max(1, page)
    limit = max(1, limit)

    # Base query with name filtering
    if name:
        query = Wishlist.query.filter(Wishlist.name == name)
    else:
        query = Wishlist.query

    # Use SQLAlchemy's pagination method
    paginated_query = query.paginate(page=page, per_page=limit, error_out=False)

    # Serialize results
    results = [wishlist.serialize() for wishlist in paginated_query.items]

    # Return response with paginated results
    return jsonify(results), status.HTTP_200_OK

######################################################################
# UPDATE AN EXISTING WISHLIST
######################################################################


@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
def update_wishlists(wishlist_id):
    """
    Update a Wishlist

    This endpoint will update a Wishlist based the body that is posted
    """
    app.logger.info("Request to Update a wishlist with id [%s]", wishlist_id)
    check_content_type("application/json")

    # Attempt to find the Wishlist and abort if not found
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' was not found.")

    # Update the Wishlist with the new data
    data = request.get_json()
    app.logger.info("Processing: %s", data)
    wishlist.deserialize(data)

    # Save the updates to the database
    wishlist.update()

    app.logger.info("Wishlist with ID: %d updated.", wishlist.id)
    return jsonify(wishlist.serialize()), status.HTTP_200_OK


# ---------------------------------------------------------------------
#                P R O D U C T  M E T H O D S
# ---------------------------------------------------------------------


######################################################################
# LIST PRODUCTS
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products", methods=["GET"])
def list_products(wishlist_id):
    """Returns all of the Products for an Wishlist"""
    app.logger.info("Request for all Products for Wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Get the products for the wishlist
    results = [product.serialize() for product in wishlist.products]

    return jsonify(results), status.HTTP_200_OK


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

    # Send the location to GET the new item
    location_url = url_for(
        "get_products", wishlist_id=wishlist.id, product_id=product.id, _external=True
    )
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
# RETRIEVE A PRODUCT FROM WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products/<int:product_id>", methods=["GET"])
def get_products(wishlist_id, product_id):
    """
    Get an Product

    This endpoint returns just an product
    """
    app.logger.info(
        "Request to retrieve Product %s for Wishlist id: %s", (product_id, wishlist_id)
    )

    # See if the product exists and abort if it doesn't
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{product_id}' could not be found.",
        )

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PRODUCT FROM WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>/products/<int:product_id>", methods=["DELETE"])
def delete_products(wishlist_id, product_id):
    """
    Delete a Product from a Wishlist

    This endpoint will remove a product entirely from the database.
    """
    app.logger.info(
        "Request to delete Product %s for Wishlist id: %s", product_id, wishlist_id
    )

    # Retrieve the wishlist
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        # If wishlist doesn't exist, consider the operation successful
        # since the product can't exist in a non-existent wishlist
        return "", status.HTTP_204_NO_CONTENT

    # Retrieve the product
    product = Product.find(product_id)
    if not product:
        # If product doesn't exist, consider deletion successful
        return "", status.HTTP_204_NO_CONTENT

    # Ensure the product is part of the wishlist
    if product not in wishlist.products:
        # If product is not in wishlist, consider deletion successful
        return "", status.HTTP_204_NO_CONTENT

    # Delete the product from the database
    product.delete()

    return "", status.HTTP_204_NO_CONTENT


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete a Wishlist

    This endpoint will delete a Wishlist based on the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)

    # Retrieve the wishlist
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        # Delete the wishlist if it exists
        wishlist.delete()

    # Return 204 regardless of whether the wishlist existed
    return "", status.HTTP_204_NO_CONTENT


######################################################################
# UPDATE A NOTE OF A PRODUCT
######################################################################


@app.route("/wishlists/<int:wishlist_id>/products/<int:product_id>/note", methods=["PATCH"])
def update_product_note(wishlist_id, product_id):
    """
    Update the note of a product in a wishlist

    This endpoint updates only the 'note' field of a product.
    """
    app.logger.info("Request to update note for Product %s in Wishlist %s", product_id, wishlist_id)
    check_content_type("application/json")

    # Retrieve the product
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    # Check if the product belongs to the given wishlist
    if product.wishlist_id != wishlist_id:
        abort(status.HTTP_400_BAD_REQUEST, "Product does not belong to the specified wishlist.")

    # Update the note field
    data = request.get_json()
    if "note" not in data:
        abort(status.HTTP_400_BAD_REQUEST, "Request must contain a 'note' field.")

    product.note = data["note"]
    product.update()

    return jsonify(product.serialize()), status.HTTP_200_OK

######################################################################
# UPDATE STATUS OF PRODUCT
######################################################################


@app.route("/wishlists/<int:wishlist_id>/products/<int:product_id>/gift", methods=["PATCH"])
def mark_product_as_gift(wishlist_id, product_id):
    """
    Mark or unmark a product in a wishlist as a gift.

    This endpoint updates the 'gift' status of a product.
    """
    app.logger.info("Request to update gift status for Product %s in Wishlist %s", product_id, wishlist_id)
    check_content_type("application/json")

    # First, find the product by ID regardless of wishlist
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    # Then check if it belongs to the specified wishlist
    if product.wishlist_id != wishlist_id:
        abort(status.HTTP_403_FORBIDDEN, "Product does not belong to the specified wishlist.")

    # Get the request data
    data = request.get_json()

    # Update the is_gift field with the provided value
    product.is_gift = data.get("is_gift", True)
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
