Feature: File listing

  Scenario: Authenticated user sees their files
    Given an authenticated user
    And the user has uploaded files
    When the user requests the file list
    Then the response contains the user's files

  Scenario: Unauthenticated user is rejected
    Given no authentication header
    When the user requests the file list
    Then the response status is 401
