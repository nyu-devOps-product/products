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
    Then I should see "Pet Demo RESTful Service" in the title
    And I should not see "404 Not Found"
