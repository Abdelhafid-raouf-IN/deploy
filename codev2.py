import requests
import json
import os

# URL de la documentation Swagger
swagger_url = "http://localhost:9090/v3/api-docs/unibank-service-pilot"

# Récupérer la documentation Swagger
response = requests.get(swagger_url)
swagger_data = response.json()

# Extraire le nom de l'API depuis le champ `info.title` dans Swagger
api_name = swagger_data.get('info', {}).get('title', 'default_api_name').replace(' ', '-').replace('-', '-')

# Dossier où les fichiers de test seront générés, basé sur le nom de l'API
output_dir = f"{api_name}"
os.makedirs(output_dir, exist_ok=True)

# Modèle de Background avec l'en-tête Feature
background_template = """
Feature: {api_name}
  Background:
    * configure ssl = true
    #-------------------------------------[ JSON FILES CALL ]-------------------------------------#
    * def baseUrl = call read ('classpath:features/JsonFile/vars.json')
    * def credentials = call read ('classpath:features/JsonFile/credentials.json')
    * def tokenResponse = call read('classpath:features/unibank-OAuth2/karate-oauth2-DEV.feature')
    #-------------------------------------[ ARGUMENTS CALL ]-------------------------------------#
    * def bridgeUnibankurlAuth2_Dev = baseUrl.authBridge
    * def accessToken = tokenResponse.response.id_token
    * url baseUrl.settingUnibankurl.dev
"""

# Modèle de scénario pour obtenir le jeton
token_request_template = """
  @ignore
  @TokenRequest
  Scenario: Get token
    #-------------------------------------[ GET TOKEN FROM karate-oauth2-DEV ]-------------------------------------#
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

# Modèle de scénario pour les requêtes REST
rest_query_template = """
  #-------------------------------------[ REST QUERIES ]-------------------------------------#
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

# Fonction pour extraire et formater le requestBody
def format_request_body(request_body):
    request_body_content = request_body.get('content', {})
    request_body_json = request_body_content.get('application/json', {}).get('schema', {})
    if '$ref' in request_body_json:
        request_body_json = swagger_data['components']['schemas'].get(request_body_json['$ref'].split('/')[-1], {})
    request_body_example = json.dumps(request_body_json, indent=2) if request_body_json else "{}"
    return f"  And request {request_body_example}"

# Fonction pour générer les tests
def generate_tests(swagger_data, api_name):
    paths = swagger_data['paths']
    for endpoint, methods in paths.items():
        for method, details in methods.items():
            summary = details.get('summary', 'No summary provided')

            # Gestion des réponses
            responses = details.get('responses', {})
            response = responses.get('200', {}).get('content', {}).get('*/*', {}).get('schema', {})
            if '$ref' in response:
                response = swagger_data['components']['schemas'].get(response['$ref'].split('/')[-1], {})
            response_example = json.dumps(response, indent=2) if response else "{}"
            
            # Gestion des requestBody
            request_body = details.get('requestBody', {})
            request_body_line = format_request_body(request_body) if request_body else ""
            
            # Gestion des paramètres supplémentaires pour les requêtes GET
            additional_params = ""
            if method == 'get' and '{id}' in endpoint:
                additional_params = f"And param id = 123"
            elif method == 'get':
                additional_params = f"And param includeDetails = true"
            
            # Nettoyer le nom du scénario pour le fichier
            scenario_name = f"{method.upper()} {endpoint.replace('{id}', '123')}"
            scenario_name_clean = scenario_name.replace('/', '_').replace(' ', '_')

            # Préparer le contenu du fichier de test avec le nom de l'API
            scenario_content = background_template.format(api_name=api_name) + token_request_template + rest_query_template.format(
                scenario_name=scenario_name,
                endpoint=endpoint,
                method=method.upper(),
                additional_params=additional_params,
                request_body=request_body_line,
                expected_status='200'  # Le statut attendu est généralement 200, mais peut être modifié selon les besoins
            )
            
            # Nom du fichier de test, incluant le nom de l'API
            filename = os.path.join(output_dir, f"{api_name}_{scenario_name_clean}.feature")

            # Assurez-vous que le répertoire existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            # Écrire le fichier de test
            with open(filename, 'w') as f:
                f.write(scenario_content)

# Générer les tests avec le nom de l'API
generate_tests(swagger_data, api_name)

print(f"Scénarios de test générés dans le dossier {output_dir}")
