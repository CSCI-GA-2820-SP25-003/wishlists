Feature: The wishlist service back-end 
  As a Online Shop Owner
  I need a RESTful wishlist service
  So that I can keep track of all my wishlists

Background:
  Given the following wishlists
    | name            | userid | products |
    | Tech Gifts      | "1001" | []       |
    | Home Decor      | "1002" | []       |
    | Office Stuff    | "1003" | []       |
    | Travel Outfits  | "1004" | []       |


Scenario: The server is running
  When I visit the "Home Page"
  Then I should see "Wishlist Manager" in the title
  And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Name" to "Wishlist 1"
    And I set the "User ID" to "1"
    # And I set the "Products" to " "
    And I press the "Create Wishlist" button
    Then I should see the message "Wishlist Created!"
    When I copy the "ID" field
    And I press the "Clear Wishlist" button
    Then the "User ID" field should be empty
    And the "Name" field should be empty
    # And the "Products" field should be empty
    When I paste the "ID" field
    And I press the "Retrieve Wishlist" button
    Then I should see the message "Wishlist Retrieved!"
    And I should see "Wishlist 1" in the "Name" field
    And I should see "1" in the "User ID" field
    # And I should see " " in the "Products" field


Scenario: List all Wishlists
    When I visit the "Home Page"
    And I press the "List Wishlists" button
    Then I should see "Tech Gifts" in the results
    Then I should see "Home Decor" in the results
    Then I should see "Office Stuff" in the results
    Then I should see "Travel Outfits" in the results

Scenario: Update the name of an existing wishlist
  When I visit the "Home Page"
  And I set the "Name" to "Old Wishlist"
  And I set the "User ID" to "2001"
  And I press the "Create Wishlist" button
  Then I should see the message "Wishlist Created!"
  When I copy the "ID" field
  And I press the "Clear Wishlist" button
  When I paste the "ID" field
  And I set the "Name" to "Updated Wishlist"
  And I press the "Update Wishlist" button
  Then I should see the message "Wishlist Updated!"
  And I should see "Updated Wishlist" in the "Name" field
