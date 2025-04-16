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

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
import os
from typing import Any
import re
import logging
import requests
from behave import given, when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60

ID_PREFIX = "wishlist_"


def save_screenshot(context: Any, filename: str) -> None:
    """Takes a snapshot of the web page for debugging and validation

    Args:
        context (Any): The session context
        filename (str): The message that you are looking for
    """
    # Remove all non-word characters (everything except numbers and letters)
    filename = re.sub(r"[^\w\s]", "", filename)
    # Replace all runs of whitespace with a single dash
    filename = re.sub(r"\s+", "-", filename)
    context.driver.save_screenshot(f"./captures/{filename}.png")


@given("the server is started")
def step_impl(context):
    context.base_url = os.getenv("BASE_URL", "http://localhost:8080")
    context.resp = requests.get(context.base_url + "/", timeout=WAIT_TIMEOUT)
    assert context.resp.status_code == 200


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # save_screenshot(context, 'Home Page')

@then('I should see "{message}" in the title')
def step_impl(context: Any, message: str) -> None:
    """Check the document title for a message"""
    assert message in context.driver.title

@then('I should not see "{text_string}"')
def step_impl(context: Any, text_string: str) -> None:
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context: Any, element_name: str, text_string: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(text_string)


@then('the "{element_name}" field should be empty')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context: Any, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clear button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when('I press the "{button}" button')
def step_impl(context: Any, button: str) -> None:
    button_id = button.lower().replace(" ", "_") + "-btn"
    context.driver.find_element(By.ID, button_id).click()

@when('I select "{value}" from the "Wishlist Dropdown"')
def step_impl(context: Any, value: str) -> None:
    select = Select(context.driver.find_element(By.ID, "select_wishlist_dropdown"))
    select.select_by_value(value)


@then('I should see "{name}" in the results')
def step_impl(context, name):
    # 1️⃣ wait until the tbody is present
    WebDriverWait(context.driver, 5).until(
        expected_conditions.presence_of_element_located((By.ID, "wishlist-results-body"))
    )

    # 2️⃣ wait until the requested wishlist name shows up
    WebDriverWait(context.driver, 5).until(
        expected_conditions.text_to_be_present_in_element((By.ID, "wishlist-results-body"), name)
    )

    # 3️⃣ final assertion (defensive – keeps the nice traceback if it still fails)
    body_text = context.driver.find_element(*(By.ID, "wishlist-results-body")).text
    assert name in body_text

@then('I should see the message "{message}"')
def step_impl(context: Any, message: str) -> None:
    # Uncomment next line to take a screenshot of the web page for debugging
    # save_screenshot(context, message)
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context: Any, text_string: str, element_name: str) -> None:
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found
