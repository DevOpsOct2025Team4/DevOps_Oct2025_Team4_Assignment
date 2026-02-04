Feature: File deletion

  Scenario: Authenticated user deletes a file
    Given an authenticated user
    And a file can be deleted
    When the user deletes the file
    Then the delete response is successful

  Scenario: File cannot be deleted
    Given an authenticated user
    And a file cannot be deleted
    When the user deletes the file
    Then the response status is 404

  Scenario: Unauthenticated user cannot delete
    Given no authentication header
    And a file can be deleted
    When the user deletes the file
    Then the response status is 401
