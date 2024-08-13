background_template = """
Feature :
  Background:
    * configure ssl = true
    * def baseUrl = call read ('classpath:features/JsonFile/vars.json')
    * def credentials = call read ('classpath:features/JsonFile/credentials.json')
    * def tokenResponse = call read('classpath:features/unibank-OAuth2/karate-oauth2-DEV.feature')
    * def bridgeUnibankurlAuth2_Dev = baseUrl.authBridge
    * def accessToken = tokenResponse.response.id_token
    * url baseUrl.settingUnibankurl.dev
"""

token_request_template = """
  @ignore
  @TokenRequest
  Scenario: Get token
    Given url bridgeUnibankurlAuth2_Dev
    And header Authorization = credentials.MR.authorization
    And header Content-Type = 'application/x-www-form-urlencoded'
    And form field grant_type = credentials.MR.grantType
    And form field username = credentials.MR.username
    And form field password = credentials.MR.password
    And form field scope = credentials.MR.scope
    When method POST
    Then status 200
    And match response == { access_token: '##string', refresh_token: '##string', scope: 'openid', id_token: '##string', token_type: 'Bearer', expires_in: '#number' }
"""

rest_query_template = """
  @Settings
  Scenario: {scenario_name}
    * def tokenRequest = call read('@TokenRequest')
    Given path '{endpoint}'
    And header Authorization = 'Bearer ' + accessToken
    {additional_params}
    {request_body}
    When method {method}
    Then status {expected_status}
    And print 'Actual response:', response
    * def responseHeaders = responseHeaders
    * def responseBody = response
    * karate.log('Response Headers:', responseHeaders)
    * karate.log('Response Body:', responseBody)
"""
