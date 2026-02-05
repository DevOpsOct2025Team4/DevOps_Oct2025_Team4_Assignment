Feature: File download

  Scenario: Authenticated user can request a download URL
    Given an authenticated user
    And a file exists for the user
    When the user requests the file download
    Then the response includes a signed download url

  Scenario: File does not exist
    Given an authenticated user
    And no file exists for the user
    When the user requests the file download
    Then the response status is 404

  Scenario: Unauthenticated user cannot download
    Given no authentication header
    And a file exists for the user
    When the user requests the file download
    Then the response status is 401
