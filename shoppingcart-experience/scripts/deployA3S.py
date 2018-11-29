import requests
import json
import base64
import os
from sys import stderr

debug = os.getenv("DEBUG", "false") == "true"

# Receiving authorization token:
print('Receiving authorization token:')
authorizationJsonBody = \
    {
        "auth": {
            "dialects": [
                os.getenv("A3S_DIALECT")
            ],
            "on-behalf-of": {
                "user-credentials": {
                    "username": os.getenv("A3S_USER"),
                    "password": os.getenv("A3S_PASSWORD")
                }
            }
        }
    }
headers = \
    {
        "Authorization": os.getenv("HEADER_AUTHORIZATION"),
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Accept-Language": os.getenv("HEADER_ACCEPT_LANGUAGE")
    }
hostname = os.getenv("A3S_SERVICE")
port = os.getenv("A3S_PORT")
url = 'http://{}:{}/asmServices/services/v1.0/auth/tokens'.format(hostname, port)
if debug:
    print('Asking for token from: {}'.format(url))
    print('With headers: {}'.format(headers))
    print('And Body: {}'.format(authorizationJsonBody))
try:
    res = requests.post(url, data=json.dumps(authorizationJsonBody), headers=headers)
    if res.status_code != 200:
        print('{} returned a bad status code: {}'.format(hostname, res.text if debug else res.status_code), stderr)
        exit(0)
except Exception as e:
    print('Error in receiving response from {} - {}'.format(hostname, e), stderr)
    exit(0)
try:
    resJson = json.loads(res.content)
except Exception as e:
    print('Error in json parsing response {}'.format(e), stderr)
    exit(0)
try:
    token = resJson['subjectToken']
except Exception as e:
    print(
        "Error: received json body do not contain 'subjectToken' property - {}".format(e),
        stderr)
    exit(0)
print('Token received {}'.format(token if debug else ""))

def a3sImportRequest(url, bodyKey, title, dataValues=""):
    print('-')
    print(dataValues)
    print('Import ms {} into A3S:'.format(title))
    headers['Authorization'] = 'Bearer ' + token
    hostname = os.getenv("A3S_SERVICE")
    port = os.getenv("A3S_PORT")

    try:
        data = base64.b64decode(os.getenv(bodyKey))
        dataJ = json.loads(data)
        if 'users' in dataJ:
            for item in dataJ["users"]:
                if 'password' in item:
                    item["password"] = dataValues
    except Exception as e:
        print('Error b64decode of {} file - {}'.format(title, e), stderr)

    url = 'http://{}:{}/asmServices/services/v1.0/{}'.format(hostname, port, url)
    if debug:
        print('Send rest: {}'.format(url))
        print('With headers: {}'.format(headers))
        print('And Body: {}'.format(data))
    try:
        res = requests.post(url, data=json.dumps(dataJ), headers=headers)

        if (res.status_code == 201 or res.status_code == 200):
            print("Successfully import/update ms {} into A3S".format(title))
        else:
            print('{} returned a bad status code: {}'.format(hostname, res.text if debug else res.status_code), stderr)
    except Exception as e:
        print('Error in import ms {} into A3S - {}'.format(title, e), stderr)

# Import ms functional roles into A3S
a3sImportRequest('load/roles', "A3S_FUNCTIONALROLES_BASE64", 'functional roles')

# Import ms api functional roles into A3S
a3sImportRequest('load/roles', "A3S_APIFUNCTIONALROLES_BASE64", 'api functional roles')

# Mapping ms functional roles and api functional roles into A3S business roles
if os.getenv("A3S_MAP_FUNCTIONAL_ROLES_TO_BUSINESS_ROLES_FLAG", "false") == "true":
    a3sImportRequest('roles/bulk', "A3S_MAP_FUNCTIONAL_ROLES_TO_BUSINESS_ROLES_BASE64", 'mapping of ms functional roles and api functional roles into A3S business roles')

# Import ms service role into A3S
a3sImportRequest('roles/bulk', "A3S_SERVICE_ROLE_BASE64", 'service role')

# Import service user into A3S
a3sImportRequest('users/bulk', "A3S_SERVICE_USER_BASE64", 'service user', os.getenv("A3S_SERVICE_USER_PASSWORD"))