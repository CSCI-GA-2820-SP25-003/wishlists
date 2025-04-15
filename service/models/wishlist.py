"""
Models for Wishlist

All of the models are stored in this module
"""

import logging

from .persistent_base import db, PersistentBase, DataValidationError
from .product import Product
logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()


class Wishlist(db.Model, PersistentBase):
    """
    Class that represents a Wishlist
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    userid = db.Column(db.String(16), nullable=False)
    products = db.relationship("Product", backref="wishlist", passive_deletes=True)

    # Completed Table Schema

    def __repr__(self):
        return f"<Wishlist {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serializes a Wishlist into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "userid": self.userid,
            "products": [product.serialize() for product in self.products],
        }

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.userid = data["userid"]
            product_list = data.get("products", [])
            for json_product in product_list:
                product = Product()
                product.deserialize(json_product)
                self.products.append(product)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained bad or no data "
                + str(error)
            ) from error
        return self
