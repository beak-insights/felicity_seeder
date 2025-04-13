import concurrent.futures
from typing import List
import random
from faker import Faker
from patients import add_patient_query, get_patient
from analysis import add_ar_query, gen_ar_request
from core import run_query, authenticate

import logging

engine = Faker()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def do_work(username):
    credentials = {
        'username': username,
        'password': "!Felicity#100" if username == 'admin' else "@Access123!",
    }
    auth_headers = authenticate(credentials)

    pt_variables, client = get_patient(username)
    pt_reg = run_query(query=add_patient_query, variables={"payload": pt_variables}, headers=auth_headers)
    logger.info(f"Created patient: {pt_reg}")
    
    # add analysis request for created patient
    ar_variables = {
        "clientRequestId": engine.ssn(),
        "clientUid": pt_variables["clientUid"],
        "clientContactUid": client["contacts"][0]["uid"],
        "patientUid": pt_reg['data']['createPatient']['uid'],
        "priority": random.choice([0, 1, 2]),
        "samples": [gen_ar_request(username) for _ in range(random.randint(1, 2))],
    }
    run_query(query=add_ar_query, variables={"payload": ar_variables}, headers=auth_headers)


def patient_plus_ar_reg(usernames: List[str], total):
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(usernames)) as executor:
        future_to_url = (executor.submit(do_work, random.choice(usernames)) for _ in range(total))

        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
                logger.info("Done")
            except Exception as exc:
                logger.error(exc)


if __name__ == '__main__':
    from users import init_users
    usernames = init_users()
    usernames = list(filter(lambda un: un not in ["admin", "system_daemon"], usernames))
    patient_plus_ar_reg(usernames, 5)
