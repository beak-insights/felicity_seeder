from random import choice
from typing import List
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_query(query=None, variables=None, headers=None):
    if not query:
        raise Exception("Query must be provided")

    request = requests.post(
        'http://0.0.0.0/felicity-gql',
        json={'query': query, 'variables': variables} if query else {
            'query': self.query, 'variables': variables},
        headers=headers,
    )
    if request.status_code == 200:
        logger.info(request.json())
        return request.json()
    else:
        raise Exception(
            f"({request.status_code}): Query Failed: {request.text}")


def authenticate(credentials: dict):
    qry = """
      mutation AuthenticateUser($username: String!, $password: String!) {
        authenticateUser(password: $password, username: $username) {
            ... on AuthenticatedData {
                token
                tokenType
            }
        }
      }
    """

    variables = credentials
    auth = run_query(query=qry, variables=variables)
    token = auth["data"]["authenticateUser"]['token']
    return {"Authorization": f"bearer {token}"}


def do_work(query: str, var_list: list, usernames: List[str] = None):
    # time.sleep(randint(1,5))
    username = choice(usernames)
    credentials = {
        'username': username,
        'password': "!Felicity#100" if username == 'admin' else "@Access123!",
    }
    auth_headers = authenticate(credentials)

    fin = []

    for variables in var_list:
        # time.sleep(randint(1, 10))
        val = run_query(query=query, variables=variables, headers=auth_headers)
        fin.append(val)

    return fin
