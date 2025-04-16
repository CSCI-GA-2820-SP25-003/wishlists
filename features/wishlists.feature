Feature: The wishlist service back-end 
  As a Online Shop Owner
  I need a RESTful wishlist service
  So that I can keep track of all my wishlists

Background:
  Given the server is started

Scenario: The server is running
  When I visit the "Home Page"
  Then I should see "Wishlist Demo REST API Service" And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Name" to "Wishlist 1"
    And I set the "User ID" to "1"
    # And I set the "Products" to " "
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Clear" button
    Then the "User ID" field should be empty
    And the "Name" field should be empty
    # And the "Products" field should be empty
    When I paste the "ID" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Wishlist 1" in the "Name" field
    And I should see "1" in the "User ID" field
    # And I should see " " in the "Products" field