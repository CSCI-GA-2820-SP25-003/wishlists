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

from decimal import Decimal, InvalidOperation
from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, Namespace, reqparse
from service.models import Wishlist, Product, DataValidationError
from service.common import status  # HTTP Status Codes

api = Api(
    app,                    # your Flask app instance
    version="1.0.0",
    title="Wishlist Demo REST API Service",
    description="A RESTful wishlist service",
    default="wishlists",
    default_label="Wishlists operations",
    prefix="/api",          # 👈 optional but highly recommended
    doc="/apidocs",         # 👈 Swagger docs
)

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
    """Base URL for our service"""
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

wishlists_ns = Namespace("wishlists", description="Operations related to Wishlists")
api.add_namespace(wishlists_ns, path="/wishlists")

create_wishlist_model = wishlists_ns.model(
    "WishlistCreate",
    {
        "name": fields.String(required=True, description="The name of the Wishlist"),
        "userid": fields.String(required=True, description="User ID of the Wishlist owner"),
    },
)

wishlist_model = wishlists_ns.inherit(
    "WishlistModel",
    create_wishlist_model,
    {
        "id": fields.Integer(readOnly=True, description="The unique ID of the Wishlist"),
        "products": fields.List(fields.Raw, description="List of products in the Wishlist"),
    },
)

wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument("name", type=str, required=False, location="args", help="Filter wishlists by name")
wishlist_args.add_argument("page", type=int, required=False, default=1, location="args", help="Page number")
wishlist_args.add_argument("limit", type=int, required=False, default=10, location="args", help="Items per page")

products_ns = Namespace("products", description="Product operations")
api.add_namespace(products_ns, path="/wishlists/<int:wishlist_id>/products")

create_product_model = products_ns.model(
    "Product",
    {
        "name": fields.String(required=True),
        "price": fields.Float(required=True),
        "quantity": fields.Integer(required=True),
        "description": fields.String(required=False),
        "note": fields.String(required=False),
        "is_gift": fields.Boolean(required=False),
        "purchased": fields.Boolean(required=False),
    },
)

product_model = products_ns.inherit(
    "ProductModel",
    create_product_model,
    {
        "id": fields.Integer(readOnly=True),
        "wishlist_id": fields.Integer(required=True),
    },
)

product_patch_model = products_ns.model(
    "ProductPatch",
    {
        "note": fields.String(required=False, description="Optional note about the product"),
        "is_gift": fields.Boolean(required=False, description="Whether the product is a gift"),
        "quantity": fields.Integer(required=False, description="Quantity of the product"),
        "purchased": fields.Boolean(required=False, description="Whether the product has been purchased"),
    }
)

product_filter_args = reqparse.RequestParser()
product_filter_args.add_argument("product_name", type=str, required=False, help="Filter products by name")
product_filter_args.add_argument("min_price", type=str, required=False, help="Minimum price filter")
product_filter_args.add_argument("max_price", type=str, required=False, help="Maximum price filter")


@wishlists_ns.route("", endpoint="wishlist_collection")
class WishlistCollection(Resource):
    """Handles all interactions with collections of Pets"""

    @wishlists_ns.doc("create_wishlist")
    @wishlists_ns.expect(create_wishlist_model)
    @wishlists_ns.response(201, "Wishlist created")
    @wishlists_ns.response(400, "Invalid Wishlist data")
    @wishlists_ns.marshal_with(wishlist_model, code=201)
    def post(self):
        """Creates a new Wishlist (with optional products)"""
        app.logger.info("Request to create a Wishlist")
        check_content_type("application/json")

        data = request.get_json()

        wishlist = Wishlist()
        try:
            wishlist.deserialize(data)
            wishlist.create()
        except DataValidationError as e:
            app.logger.error("Wishlist creation failed: %s", str(e))
            abort(status.HTTP_400_BAD_REQUEST, description=str(e))

        location_url = url_for("wishlist_resource", wishlist_id=wishlist.id, _external=True)
        return wishlist.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    @wishlists_ns.doc("list_wishlists")
    @wishlists_ns.expect(wishlist_args)
    @wishlists_ns.marshal_list_with(wishlist_model)
    def get(self):
        """Returns paginated Wishlists with optional name filtering"""
        app.logger.info("Request for Wishlists list")

        args = wishlist_args.parse_args()
        name = args.get("name")
        page = max(1, args.get("page", 1))
        limit = max(1, args.get("limit", 10))

        query = Wishlist.query
        if name:
            query = query.filter(Wishlist.name == name)

        paginated = query.paginate(page=page, per_page=limit, error_out=False)

        return [wishlist.serialize() for wishlist in paginated.items], status.HTTP_200_OK


@wishlists_ns.route("/<int:wishlist_id>", endpoint="wishlist_resource")
class WishlistResource(Resource):
    """Handles all interactions with collections of Pets"""
    @wishlists_ns.doc("get_wishlist")
    @wishlists_ns.response(200, "Wishlist retrieved successfully")
    @wishlists_ns.response(404, "Wishlist not found")
    @wishlists_ns.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """Retrieve a Wishlist by its ID"""
        app.logger.info("Request for Wishlist with id: %s", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, description=f"Wishlist with id '{wishlist_id}' could not be found.")

        return wishlist.serialize(), status.HTTP_200_OK

    @wishlists_ns.doc("delete_wishlist")
    @wishlists_ns.response(204, "Wishlist deleted")
    def delete(self, wishlist_id):
        """Delete a Wishlist by ID"""
        app.logger.info("Request to delete wishlist with id: %s", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
            app.logger.info("Wishlist with id [%s] was deleted", wishlist_id)

        # Return 204 regardless of whether the wishlist existed
        return "", status.HTTP_204_NO_CONTENT

    @wishlists_ns.doc("update_wishlist")
    @wishlists_ns.response(200, "Wishlist updated successfully")
    @wishlists_ns.response(400, "Missing required field: name")
    @wishlists_ns.response(404, "Wishlist not found")
    @wishlists_ns.expect(create_wishlist_model)  # reuses existing input model
    @wishlists_ns.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """Update a Wishlist (only 'name' is allowed to change)"""
        app.logger.info("Request to update Wishlist with id [%s]", wishlist_id)
        check_content_type("application/json")

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, description=f"Wishlist with id '{wishlist_id}' was not found.")

        data = request.get_json()
        app.logger.debug("Payload = %s", data)

        if "name" not in data:
            abort(status.HTTP_400_BAD_REQUEST, description="Missing required field: name")

        wishlist.name = data["name"]
        wishlist.update()

        return wishlist.serialize(), status.HTTP_200_OK


@products_ns.route("", endpoint="product_collection")
class ProductCollection(Resource):
    """Handles all interactions with collections of Pets"""
    @products_ns.doc("create_product")
    @products_ns.expect(create_product_model)
    @products_ns.response(201, "Product created")
    @products_ns.response(400, "Invalid data")
    @products_ns.response(404, "Wishlist not found")
    @products_ns.marshal_with(product_model, code=201)
    def post(self, wishlist_id):
        """Create a new Product in a Wishlist"""
        app.logger.info("Request to create Product for Wishlist with id: %s", wishlist_id)
        check_content_type("application/json")

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, description=f"Wishlist with id '{wishlist_id}' could not be found.")

        product = Product()
        try:
            product.deserialize(request.get_json())
        except DataValidationError as e:
            abort(status.HTTP_400_BAD_REQUEST, description=f"Invalid product data: {e}")

        wishlist.products.append(product)
        wishlist.update()

        location_url = url_for("product_resource", wishlist_id=wishlist.id, product_id=product.id, _external=True)
        return product.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    @products_ns.doc("list_products")
    @products_ns.expect(product_filter_args)
    @products_ns.marshal_list_with(product_model)
    def get(self, wishlist_id):
        """Returns all Products for a Wishlist, optionally filtered by name and price"""
        app.logger.info("Request for all Products for Wishlist with id: %s", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, description=f"Wishlist with id '{wishlist_id}' could not be found.")

        args = product_filter_args.parse_args()
        name_filter = (args.get("product_name") or "").strip().lower()

        # Parse and validate min_price and max_price
        try:
            min_price = Decimal(args.get("min_price")) if args.get("min_price") else None
        except (ValueError, TypeError, InvalidOperation):
            abort(status.HTTP_400_BAD_REQUEST, description="Invalid min_price parameter. Must be a valid number.")

        try:
            max_price = Decimal(args.get("max_price")) if args.get("max_price") else None
        except (ValueError, TypeError, InvalidOperation):
            abort(status.HTTP_400_BAD_REQUEST, description="Invalid max_price parameter. Must be a valid number.")

        # Apply filters
        filtered = [
            p for p in wishlist.products
            if (not name_filter or name_filter in p.name.lower())
            and (min_price is None or p.price >= min_price)
            and (max_price is None or p.price <= max_price)
        ]

        return [p.serialize() for p in filtered], status.HTTP_200_OK


@products_ns.route("/<int:product_id>", endpoint="product_resource")
@products_ns.param("wishlist_id", "The Wishlist ID")
@products_ns.param("product_id", "The Product ID")
class ProductResource(Resource):
    """Handles all interactions with collections of Pets"""
    @products_ns.doc("get_product")
    @products_ns.response(200, "Product retrieved")
    @products_ns.response(403, "Product does not belong to the specified wishlist")
    @products_ns.response(404, "Product not found")
    @products_ns.marshal_with(product_model)
    def get(self, wishlist_id, product_id):
        """Retrieve a single Product by its ID within a Wishlist"""
        app.logger.info("Request to retrieve Product %s for Wishlist id: %s", product_id, wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, description=f"Wishlist with id '{wishlist_id}' was not found.")

        product = Product.find(product_id)
        if not product:
            abort(status.HTTP_404_NOT_FOUND, description=f"Product with id '{product_id}' was not found.")

        # Make sure the product belongs to the correct wishlist
        if product.wishlist_id != wishlist.id:
            abort(status.HTTP_403_FORBIDDEN, description="Product does not belong to the specified wishlist.")

        return product.serialize(), status.HTTP_200_OK

    @products_ns.doc("delete_product")
    @products_ns.response(204, "Product deleted")
    @products_ns.response(403, "Product does not belong to the specified wishlist")
    def delete(self, wishlist_id, product_id):
        """Delete a Product from a Wishlist"""
        app.logger.info("Request to delete Product %s for Wishlist id: %s", product_id, wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            return "", status.HTTP_204_NO_CONTENT

        product = Product.find(product_id)
        if not product:
            return "", status.HTTP_204_NO_CONTENT

        # Make sure the product is linked to this wishlist
        if product not in wishlist.products:
            return "", status.HTTP_204_NO_CONTENT  # or use 403 if you prefer stricter validation

        product.delete()
        app.logger.info("Product with id [%s] deleted", product_id)
        return "", status.HTTP_204_NO_CONTENT

    @products_ns.doc("patch_product")
    @products_ns.expect(product_patch_model)
    @products_ns.response(200, "Product updated successfully")
    @products_ns.response(204, "Product deleted due to quantity = 0")
    @products_ns.response(400, "Invalid product data")
    @products_ns.response(403, "Product does not belong to the specified wishlist")
    @products_ns.response(404, "Product not found")
    @products_ns.marshal_with(product_model)
    def patch(self, wishlist_id, product_id):
        """Partial update of a Product (note, is_gift, quantity, purchased)"""
        app.logger.info("Request to partially update Product %s in Wishlist %s", product_id, wishlist_id)
        check_content_type("application/json")

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' not found.")

        product = Product.find(product_id)
        if not product:
            abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' not found.")

        if product.wishlist_id != wishlist.id:
            abort(status.HTTP_403_FORBIDDEN, "Product does not belong to the specified wishlist.")

        data = request.get_json()
        if not data:
            abort(status.HTTP_400_BAD_REQUEST, "Request must contain data")

        allowed_fields = {"note", "is_gift", "quantity", "purchased"}
        if not any(f in data for f in allowed_fields):
            abort(status.HTTP_400_BAD_REQUEST, "PATCH must include note, is_gift, quantity, or purchased")

        for field in allowed_fields:
            if field in data:
                setattr(product, field, data[field])

        if "quantity" in data:
            if data["quantity"] == 0:
                product.delete()
                return "", status.HTTP_204_NO_CONTENT
            if not isinstance(data["quantity"], int) or data["quantity"] < 0:
                abort(status.HTTP_400_BAD_REQUEST, "Quantity must be a non-negative integer")

        product.update()
        return product.serialize(), status.HTTP_200_OK

    @products_ns.doc("put_product")
    @products_ns.expect(create_product_model)
    @products_ns.marshal_with(product_model)
    def put(self, wishlist_id, product_id):
        """Full update of a Product (PUT)"""
        app.logger.info("Request to fully update Product %s in Wishlist %s", product_id, wishlist_id)
        check_content_type("application/json")

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, f"Wishlist with id '{wishlist_id}' not found.")

        product = Product.find(product_id)
        if not product:
            abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' not found.")

        if product.wishlist_id != wishlist.id:
            abort(status.HTTP_403_FORBIDDEN, "Product does not belong to the specified wishlist.")

        data = request.get_json()
        if not data:
            abort(status.HTTP_400_BAD_REQUEST, description="Missing product data")

        required_fields = ["name", "price", "quantity", "description"]
        missing = [f for f in required_fields if f not in data]
        if missing:
            abort(status.HTTP_400_BAD_REQUEST, f"Missing required fields: {', '.join(missing)}")

        product.name = data["name"]
        product.price = data["price"]
        product.quantity = data["quantity"]
        product.description = data["description"]
        product.note = data.get("note", product.note)
        product.is_gift = data.get("is_gift", False if product.is_gift is None else product.is_gift)
        product.purchased = data.get("purchased", product.purchased)

        product.update()
        return product.serialize(), status.HTTP_200_OK


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
