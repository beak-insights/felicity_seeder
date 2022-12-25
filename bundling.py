import concurrent.futures
from typing import List
import random
from faker import Faker
from patients import add_patient_query, patient_variables
from analysis import add_ar_query, gen_sample
from core import run_query, authenticate

import logging

engine = Faker()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def do_work(query: str = None, var_list: list = None, usernames: List[str] = None):
    # time.sleep(randint(1,5))

    username = random.choice(usernames)
    credentials = {
        'username': username,
        'password': "!Felicity#100",
    }
    auth_headers = authenticate(credentials)

    for variables in var_list:
        # time.sleep(randint(1, 10))
        pt_reg = run_query(query=query, variables=variables,
                           headers=auth_headers)

        logger.info(f"Created patient: {pt_reg}")
        # add analysis request for created patient
        ar_variables = {
            "payload": {
                "clientRequestId": engine.ssn(),
                "clientUid": random.randint(1, 1500),
                "clientContactUid": 1,
                "patientUid": pt_reg['data']['createPatient']['uid'],
                "priority": random.choice([0, 2]),
                "samples": [gen_sample() for _x in range(random.randint(1, 2))],
            }
        }
        run_query(query=add_ar_query, variables=ar_variables,
                  headers=auth_headers)


def patient_plus_ar_reg(usernames: List[str]):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = (executor.submit(do_work, add_patient_query,
                         variables, usernames) for variables in patient_variables)

        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
                logger.info("Done")
            except Exception as exc:
                logger.error(exc)
