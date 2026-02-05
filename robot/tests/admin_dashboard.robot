*** Settings ***
Library    SeleniumLibrary    timeout=10
Library    OperatingSystem

Suite Setup    Open Login Page
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}    http://localhost:5173
${BROWSER}     headlesschrome
${ADMIN_USERNAME}    ${EMPTY}
${ADMIN_PASSWORD}    ${EMPTY}
${NEW_USER_EMAIL}    ${EMPTY}
${NEW_USER_PASSWORD}    ${EMPTY}
${NEW_ADMIN_EMAIL}    ${EMPTY}
${NEW_ADMIN_PASSWORD}    ${EMPTY}

*** Keywords ***
Open Login Page
    Resolve Base Url
    Open Browser    ${BASE_URL}/login    ${BROWSER}
    Set Window Size    1280    800
    Go To Login Page

Resolve Base Url
    ${env_base}=    Get Environment Variable    ROBOT_BASE_URL    default=${BASE_URL}
    Set Suite Variable    ${BASE_URL}    ${env_base}
    ${env_browser}=    Get Environment Variable    ROBOT_BROWSER    default=${BROWSER}
    Set Suite Variable    ${BROWSER}    ${env_browser}
    ${env_admin_user}=    Get Environment Variable    ROBOT_ADMIN_USERNAME    default=
    ${env_admin_pass}=    Get Environment Variable    ROBOT_ADMIN_PASSWORD    default=
    Set Suite Variable    ${ADMIN_USERNAME}    ${env_admin_user}
    Set Suite Variable    ${ADMIN_PASSWORD}    ${env_admin_pass}

Require Admin Credentials
    Run Keyword If    '${ADMIN_USERNAME}' == '' or '${ADMIN_PASSWORD}' == ''    Skip    ROBOT_ADMIN_USERNAME/ROBOT_ADMIN_PASSWORD not set

Go To Login Page
    Go To    ${BASE_URL}/login
    Wait Until Page Contains Element    css:input#email

Login With Credentials
    [Arguments]    ${email}    ${password}
    Go To Login Page
    Input Text    css:input#email    ${email}
    Input Password    css:input#password    ${password}
    Click Button    css:button[type="submit"]

Wait For Admin Dashboard
    Wait Until Page Contains Element    xpath://h1[normalize-space()="Admin Dashboard"]

Ensure Admin Logged In
    Require Admin Credentials
    Login With Credentials    ${ADMIN_USERNAME}    ${ADMIN_PASSWORD}
    Wait For Admin Dashboard

Wait For User Dashboard
    Wait Until Page Contains Element    xpath://h1[contains(., "File Dashboard")]

Open Create User Form
    ${open}=    Run Keyword And Return Status    Page Should Contain Element    xpath://form//h3[contains(., "Create New User")]
    IF    not ${open}
        Click Button    xpath://button[normalize-space()="+ Create User"]
    END
    Wait Until Page Contains Element    xpath://form//h3[contains(., "Create New User")]

Create Admin User
    [Arguments]    ${email}    ${password}
    Open Create User Form
    Input Text    xpath://form//input[@type="email"]    ${email}
    Input Password    xpath://form//input[@type="password"]    ${password}
    Select From List By Value    xpath://form//select    admin
    Click Button    xpath://form//button[normalize-space()="Create User"]
    Wait Until Page Contains Element    xpath://tr[.//td[normalize-space()="${email}"] and .//span[normalize-space()="admin"]]

Create Standard User
    [Arguments]    ${email}    ${password}
    Open Create User Form
    Input Text    xpath://form//input[@type="email"]    ${email}
    Input Password    xpath://form//input[@type="password"]    ${password}
    Select From List By Value    xpath://form//select    user
    Click Button    xpath://form//button[normalize-space()="Create User"]
    Wait Until Page Contains Element    xpath://tr[.//td[normalize-space()="${email}"] and .//span[normalize-space()="user"]]

Delete User By Email
    [Arguments]    ${email}
    ${row}=    Set Variable    //tr[.//td[normalize-space()="${email}"]]
    Wait Until Page Contains Element    xpath:${row}    timeout=10
    Click Button    xpath:${row}//button[normalize-space()="Delete"]
    Wait Until Page Contains Element    xpath://h3[normalize-space()="Confirm Delete"]    timeout=10
    Click Button    xpath://h3[normalize-space()="Confirm Delete"]/ancestor::div[contains(@class, "bg-white")]//button[normalize-space()="Delete"]
    Wait Until Page Does Not Contain Element    xpath:${row}    timeout=15

Logout From Dashboard
    Click Button    xpath://button[normalize-space()="Logout"]
    Wait Until Page Contains Element    css:input#email    timeout=10

*** Test Cases ***
ADMIN-CreateUser
    Ensure Admin Logged In
    ${ts}=    Get Time    epoch
    ${user_email}=    Set Variable    robot-user-${ts}@example.com
    ${admin_email}=    Set Variable    robot-admin-${ts}@example.com
    ${user_password}=    Set Variable    UserPass123!
    ${admin_password}=    Set Variable    AdminPass123!

    Set Suite Variable    ${NEW_USER_EMAIL}    ${user_email}
    Set Suite Variable    ${NEW_USER_PASSWORD}    ${user_password}
    Set Suite Variable    ${NEW_ADMIN_EMAIL}    ${admin_email}
    Set Suite Variable    ${NEW_ADMIN_PASSWORD}    ${admin_password}

    Create Standard User    ${NEW_USER_EMAIL}    ${NEW_USER_PASSWORD}
    Create Admin User    ${NEW_ADMIN_EMAIL}    ${NEW_ADMIN_PASSWORD}
    Logout From Dashboard

ADMIN-VerifyUserCreation
    Should Not Be Empty    ${NEW_USER_EMAIL}
    Login With Credentials    ${NEW_USER_EMAIL}    ${NEW_USER_PASSWORD}
    Wait For User Dashboard
    Logout From Dashboard

    Ensure Admin Logged In
    Delete User By Email    ${NEW_USER_EMAIL}
    Logout From Dashboard

ADMIN_VerifyAdminCreation
    Should Not Be Empty    ${NEW_ADMIN_EMAIL}
    Login With Credentials    ${NEW_ADMIN_EMAIL}    ${NEW_ADMIN_PASSWORD}
    Wait For Admin Dashboard
    Logout From Dashboard

    Ensure Admin Logged In
    Delete User By Email    ${NEW_ADMIN_EMAIL}
    Logout From Dashboard
