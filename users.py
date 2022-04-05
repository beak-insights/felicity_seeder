import concurrent.futures
from typing import List
from faker import Faker
import requests
import random
import time
from core import run_query, authenticate, do_work
import json

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = Faker()

user_names = []

add_user_mutation = """
  mutation AddUser(
      $firstName: String!,
      $lastName: String!,
      $email: String!,
      $openReg: Boolean
    ){
    createUser(
      firstName: $firstName,
      lastName: $lastName,
      email: $email,
      openReg: $openReg,
    ) {
        ... on UserType {
            uid
            firstName
            lastName
        }
        ... on OperationError {
            error
        }
    }
}
"""

add_auth_mutation = """
  mutation AddUserAuth(
      $userUid: Int!,
      $userName: String!,
      $password: String!,
      $passwordc: String!
    ){
    createUserAuth(
      userUid: $userUid,
      userName: $userName,
      password: $password,
      passwordc: $passwordc,
    ) {
        ... on UserType {
            uid
            auth {
                userName
            }
        }
        ... on OperationError {
            error
        }
    }
}
"""

fetch_users = """
    query {
    userAll {
        items {
        auth {
            userName
        }
        }
    }
    }
"""

_unique = []
def user_faker():
    
    while True:
        fist_name = engine.first_name()
        last_name = engine.last_name()
        if fist_name not in _unique:
            _unique.append(fist_name)
            break
        
    return {
        'firstName': fist_name,
        'lastName': last_name,
        'email': f"{fist_name}{last_name}@felcity.com".lower(),
        'openReg': False,
    } 
    

fake_users = [user_faker() for i in range(10)]


def start_user_reg(usernames: List[str]):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = (executor.submit(do_work, add_user_mutation, fake_users, usernames) for i in [1])

        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
                # add authentication details to registered users
                auth_vars = [
                    {
                        'userUid': item["data"]["createUser"]["uid"],
                        'userName': item["data"]["createUser"]["firstName"].lower(),
                        'password': 'password',
                        'passwordc': 'password',
                    } for item in data
                ]
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_url = (executor.submit(do_work, add_auth_mutation, auth_vars, usernames) for i in [1])
                    for future in concurrent.futures.as_completed(future_to_url):
                        try:
                            data = future.result()
                        except Exception as exc:
                            logger.error(exc)

                logger.info(f'Done!!')
            except Exception as exc:
                logger.error(exc)


def fetch_user_auths(usernames: List[str]):
    users = do_work(fetch_users, [{}], usernames)
    for user in users[0]["data"]["userAll"]["items"]:
        print(user)
    user_names = [user["auth"]["userName"] for user in users[0]["data"]["userAll"]["items"] if user["auth"]]
    # logger.info(f'user_names: {user_names}')
    return user_names