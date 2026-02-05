*** Settings ***
Library    SeleniumLibrary    timeout=10
Library    OperatingSystem

Suite Setup    Open Login Page
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}    http://localhost:5173
${BROWSER}     headlesschrome
${USERNAME}    ${EMPTY}
${PASSWORD}    ${EMPTY}

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
    ${env_user}=    Get Environment Variable    ROBOT_USERNAME    default=
    ${env_pass}=    Get Environment Variable    ROBOT_PASSWORD    default=
    Set Suite Variable    ${USERNAME}    ${env_user}
    Set Suite Variable    ${PASSWORD}    ${env_pass}

Go To Login Page
    Go To    ${BASE_URL}/login
    Wait Until Page Contains Element    css:input#email

Require Credentials
    Run Keyword If    '${USERNAME}' == '' or '${PASSWORD}' == ''    Skip    ROBOT_USERNAME/ROBOT_PASSWORD not set

Ensure Logged In
    Require Credentials
    Go To Login Page
    Login With Staging Credentials
    Wait Until Page Contains Element    xpath://h1[contains(., "File Dashboard") or contains(., "Admin Dashboard")]    timeout=15

Login With Staging Credentials
    Input Text    css:input#email    ${USERNAME}
    Input Password    css:input#password    ${PASSWORD}
    Click Button    css:button[type="submit"]
    Wait Until Page Contains Element    xpath://h1[contains(., "File Dashboard") or contains(., "Admin Dashboard")]    timeout=15

Create Temp Upload File
    ${ts}=    Get Time    epoch
    ${filename}=    Set Variable    robot-upload-${ts}.txt
    ${filepath}=    Join Path    ${OUTPUT DIR}    ${filename}
    Create File    ${filepath}    hello from robot
    RETURN    ${filename}    ${filepath}

Upload File And Wait
    [Arguments]    ${filepath}    ${filename}
    Choose File    css:input[type="file"]    ${filepath}
    Click Button    xpath://button[normalize-space()="Upload File"]
    Wait Until Page Contains    ${filename}    timeout=20

Find File Row
    [Arguments]    ${filename}
    ${row}=    Set Variable    //tr[.//*[normalize-space()="${filename}"]]
    Wait Until Page Contains Element    xpath:${row}    timeout=10
    RETURN    ${row}

Download File From Row
    [Arguments]    ${row}
    Click Button    xpath:${row}//button[contains(., "Download")]
    Sleep    1s
    Page Should Not Contain    Download failed

Delete File From Row
    [Arguments]    ${row}
    Click Button    xpath:${row}//button[contains(., "Delete")]
    Handle Alert    accept
    Wait Until Page Does Not Contain Element    ${row}    timeout=15

Logout From Dashboard
    Click Button    xpath://button[contains(., "Logout")]
    Wait Until Page Contains Element    css:input#email    timeout=10

*** Test Cases ***
Login Page Renders
    Go To Login Page
    Page Should Contain    Log In
    Page Should Contain Element    css:input#email
    Page Should Contain Element    css:input#password
    Page Should Contain Element    css:button[type="submit"]

Login With Staging Secrets
    Require Credentials
    Go To Login Page
    Login With Staging Credentials

Upload Download Delete File
    Require Credentials
    Ensure Logged In
    ${filename}    ${filepath}=    Create Temp Upload File
    Upload File And Wait    ${filepath}    ${filename}
    ${row}=    Find File Row    ${filename}
    Download File From Row    ${row}
    Delete File From Row    ${row}

Logout Works
    Require Credentials
    Ensure Logged In
    Logout From Dashboard
