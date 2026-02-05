Feature: File upload

  Scenario: Authenticated user uploads a file successfully
    Given an authenticated user
    And a file ready to upload
    When the user uploads the file
    Then the upload response includes the stored path

  Scenario: Missing file in request
    Given an authenticated user
    When the user uploads without a file
    Then the response status is 400

  Scenario: Unauthenticated user cannot upload
    Given no authentication header
    And a file ready to upload
    When the user uploads the file
    Then the response status is 401
