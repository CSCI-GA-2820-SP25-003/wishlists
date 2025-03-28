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
class Product(db.Model, PersistentBase):
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
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Numeric price with 2 decimal places
    description = db.Column(db.String(255))  # Increased length for better descriptions

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}] wishlist[{self.wishlist_id}]>"

    def __str__(self):
        return (
            f"{self.name}: {self.price}, {self.description}"
        )

    def serialize(self) -> dict:
        """Converts a Product into a dictionary"""
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
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
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
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
