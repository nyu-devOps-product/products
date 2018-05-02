Feature: The product service back-end
    As a Product manager
    I need a RESTful catalog service
    So that I can keep track of all products in my inventory


Background:
    Given the following products
    | id | name       | price    | image_id  | description     |
    |  1 | iPhone     | 849      | img_001   | Latest model    |
    |  2 | Samsung    | 749      | img_002   | Latest model    |
    |  3 | Speaker    | 149      | img_003   | Latest model    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Products RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: List all products
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "iPhone" in the results
    And I should see "Samsung" in the results
    And I should see "Speaker" in the results

Scenario: Read a product
    When I visit the "Home Page"
    And I change "Id" to "3"
    And I press the "Retrieve" button
    Then I should see "Speaker" in the "Name" field

Scenario: Create a product
    When I visit the "Home Page"
    And I change "Name" to "HDTV"
    And I change "Price" to "449"
    And I press the "Create" button
    Then I should see the message "Success"
    When I press the "Search" button
    Then I should see "HDTV" in the results

Scenario: Update a product
    When I visit the "Home Page"
    And I change "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "iPhone" in the "Name" field
    When I change "Name" to "Apple phone 8"
    And I press the "Update" button
    And I press the "Clear" button
    And I change "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "Apple phone 8" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "Apple phone 8" in the results
    And I should not see "iPhone" in the results

Scenario: Delete a product
    When I visit the "Home Page"
    And I change "Id" to "3"
    And I press the "Retrieve" button
    Then I should see "Speaker" in the "Name" field
    When I press the "Delete" button
    Then I should see the message "Product with ID [3] has been Deleted!"
    When I press the "Search" button
    Then I should see "iPhone" in the results
    And I should see "Samsung" in the results
    And I should not see "Speaker" in the results

Scenario: Query a product by keyword
    When I visit the "Home Page"
    And I change "Name" to "Samsung"
    And I press the "Search" button
    Then I should see "Samsung" in the results
    And I should not see "Speaker" in the results
    And I should not see "iPhone" in the results

Scenario: Action on a product - Post review
    When I visit the "Home Page"
    And I change "Id" to "1"
    And I press the "Retrieve" button
    Then I should see "iPhone" in the "Name" field
    When I change "Username" to "Grumpy_user"
    And I change "Score" to "1"
    And I press the "Review" button
    And I press the "Clear" button
    And I change "Name" to "iPhone"
    And I press the "Search" button
    Then I should see "iPhone" in the results
    And I should see "username: Grumpy_user" in the results
    And I should see "score: 1" in the results
