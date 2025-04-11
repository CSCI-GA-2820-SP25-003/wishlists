Feature: The wishlist service back-end 
  As a Online Shop Owner
  I need a RESTful wishlist service
  So that I can keep track of all my wishlists

Background:
  Given the server is started

Scenario: The server is running
  When I visit the "home page"
  Then I should see "Wishlist REST API Service" And I should not see "404 Not Found"