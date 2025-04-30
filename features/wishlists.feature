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

  Given the following products
    | name            | price | quantity | min_price | max_price | description   | note   | is_gift | purchased |
    | Air Fryer       | 9000  | 1        | 1         | 10000     | air fryer     | note 1 | True    | False     |
    | Banana Slicer   | 10    | 24       | 1         | 100       | banana slicer | note 2 | False   | False     |



Scenario: The server is running
  When I visit the "Home Page"
  Then I should see "Wishlist Manager" in the title
  And I should not see "404 Not Found"

Scenario: Create a Wishlist
    When I visit the "Home Page"
    And I set the "Name" to "Wishlist 1"
    And I set the "User ID" to "1"
    And I press the "Create Wishlist" button
    Then I should see the message "Wishlist Created!"
    When I copy the "ID" field
    And I press the "Clear Wishlist" button
    Then the "User ID" field should be empty
    And the "Name" field should be empty
    When I paste the "ID" field
    And I press the "Retrieve Wishlist" button
    Then I should see the message "Wishlist Retrieved!"
    And I should see "Wishlist 1" in the "Name" field
    And I should see "1" in the "User ID" field


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

Scenario: Delete a Wishlist
  When I visit the "Home Page"
  And I set the "Name" to "Old Wishlist"
  And I set the "User ID" to "2001"
  And I press the "Create Wishlist" button
  When I copy the "ID" field
  And I press the "Clear Wishlist" button
  When I paste the "ID" field
  And I press the "Delete Wishlist" button
  Then I should see the message "Wishlist Deleted!"

Scenario: Search for a wishlist by name
  When I visit the "Home Page"
  And I set the "Name" to "Office Stuff"
  When I press the "Search Wishlist" button
  Then I should see "Office Stuff" in the results

# Scenario: Retrieve a product from a wishlist
#   When I visit the "Home Page"
#   And I select "Home Decor" from the "Wishlist Dropdown"
#   And I set the product "Name" to "Rope"
#   And I set the product "Price" to "3"
#   And I press the "Create Product" button
#   And I copy the product "ID" field
#   And I press the "Clear Product" button
#   And I paste the product "ID" field
#   And I press the "Retrieve Product" button
#   Then I should see "Rope" in the product "Name" field

Scenario: Filter products by name
  When I visit the "Home Page"
  And I select "Tech Gifts" from the "Wishlist Dropdown"
  And I press the "List Products" button
  And I set the product "Filter By Name" to "Air Fryer"
  And I press the "Filter Product" button
  Then I should see the product "Air Fryer" in the results
  And I should not see the product "Banana Slicer" in the results


Scenario: Update a Product
    When I visit the "Home Page"
    And I select "Tech Gifts" from the "Wishlist Dropdown"
    And I set the product "Name" to "Air Fryer"
    And I press the "Search Product" button
    Then I should see the message "All products loaded successfully"
    And I should see "Air Fryer" in the product "Name" field
    And I should see "air fryer" in the product "Description" field
    When I change the product "Name" to "Fryer Air"
    And I press the "Update Product" button
    Then I should see the message "Product Updated!"
    When I copy the product "ID" field
    And I press the "Clear Product" button
    And I paste the product "ID" field
    And I press the "Retrieve Product" button
    Then I should see "Fryer Air" in the product "Name" field
    When I press the "Clear Product" button
    And I press the "Search Product" button
    Then I should see the message "All products loaded successfully"
    And I should see the product "Fryer Air" in the results
    And I should not see the product "Air Fryer" in the results
