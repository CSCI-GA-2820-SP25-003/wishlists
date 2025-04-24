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
Persistent Base class for database CRUD functions
"""

import logging
from .persistent_base import db, PersistentBase, DataValidationError

logger = logging.getLogger("flask.app")


######################################################################
#  PRODUCT   M O D E L
######################################################################
class Product(db.Model, PersistentBase):  # pylint: disable=too-many-instance-attributes
    """
    Class that represents an Product
    """

    __tablename__ = "products"  # Define table name explicitly

    # Table Schema

    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(
        db.Integer, db.ForeignKey("wishlist.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(64), nullable=False)  # Product name
    price = db.Column(
        db.Numeric(10, 2), nullable=False
    )  # Numeric price with 2 decimal places
    description = db.Column(db.String(255))  # Increased length for better descriptions
    quantity = db.Column(db.Integer, default=1)
    note = db.Column(db.String(255), nullable=True)  # Field for the note
    is_gift = db.Column(db.Boolean, default=False)
    purchased = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}] wishlist[{self.wishlist_id}]>"

    def __str__(self):
        return f"{self.name}: {self.price}, {self.description}"

    def serialize(self) -> dict:
        """Converts a Product into a dictionary"""
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "name": self.name,
            "price": float(self.price),
            "description": self.description,
            "quantity": self.quantity,
            "note": self.note,
            "is_gift": self.is_gift if self.is_gift is not None else False,
            "purchased": self.purchased if self.purchased is not None else False,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wishlist_id = data["wishlist_id"]
            self.name = data["name"]
            self.price = data["price"]
            self.description = data["description"]
            self.quantity = data["quantity"]
            self.note = data["note"] or None
            self.is_gift = data["is_gift"] or False
            self.purchased = data["purchased"] or False
        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data "
                + str(error)
            ) from error

        return self
