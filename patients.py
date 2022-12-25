import concurrent.futures
from faker import Faker
import requests
import random
import time
from core import run_query, authenticate, do_work

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = Faker()

add_patient_query = """
  mutation AddPatient($payload: PatientInputType!){
  createPatient(payload: $payload) {
    ... on PatientType {
        uid
    }
    ... on OperationError {
        error
    }
  }
}
"""

patient_variables = [  # list of lists - each list will be run in its own thread -> simulating multi user regs
    [
        {
            'payload': {
                'clientPatientId': engine.ssn(),
                'firstName': engine.first_name(),
                'middleName': engine.first_name(),
                'lastName': engine.last_name(),
                'age': random.randint(1, 90),
                'gender': random.choice(["Male", "Female"]),
                'dateOfBirth': str(engine.date_time()),
                'ageDobEstimated': engine.boolean(),
                'clientUid': 1,
                'phoneMobile': engine.phone_number(),
                'phoneHome': engine.phone_number(),
                'consentSms': engine.boolean(),
            }
        } for i in range(100)
    ] for x in range(10000)
]

# def do_work1(var_list):
#     auth_headers = authenticate()
#
#     for variables in var_list:
#         run_query(query=add_patient_query, variables=variables, headers=auth_headers)
#


def start_patient_reg():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = (executor.submit(do_work, add_patient_query, variables)
                         for variables in patient_variables)

        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
                logger.info("Done")
            except Exception as exc:
                logger.error(exc)
