# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
import os
import requests
from behave import given, when, then  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

WAIT_TIMEOUT = 60


@given("the server is started")
def step_impl(context):
    context.base_url = os.getenv("BASE_URL", "http://localhost:8080")
    context.resp = requests.get(context.base_url + "/", timeout=WAIT_TIMEOUT)
    assert context.resp.status_code == 200


@when('I visit the "Home Page"')
def step_impl(context: Any) -> None:
    """Make a call to the base URL"""
    context.driver.get(context.base_url)


@then('I should see "{message}" And I should not see "{text_string}"')
def step_impl(context, message, text_string):
    assert message in str(context.resp.text)
    assert text_string not in str(context.resp.text)
