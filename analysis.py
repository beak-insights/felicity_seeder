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

add_ar_query = """
mutation AddAnalysisRequest ($payload: AnalysisRequestInputType!) {
  createAnalysisRequest(payload: $payload) {
      ... on AnalysisRequestWithSamples {
        uid
      }
      ... on OperationError {
          error
      }
  }
}
"""


def gen_sample():
    randoms = [
        {
            "sampletypes": [2, 3],
            "analyses": [None, 1, 2, 3],
            "profiles": [None, 1, 2, 3, 4],
        },
        {
            "sampletypes": [4],
            "analyses": [3],
            "profiles": [None],
        },
    ]

    while True:
        selected = random.choice(randoms)
        s_typ = random.choice(selected.get("sampletypes"))
        anal = random.choice(selected.get("analyses"))
        prof = random.choice(selected.get("profiles"))

        if anal or prof:
            break

    return {
        "sampleType": s_typ,
        "profiles": [prof] if prof else [],
        "analyses": [anal] if anal else []
    }


ar_variables = [  # list of lists - each list will be run in its own thread -> simulating multi user regs
    [
        {
            "payload": {
                "clientRequestId": engine.ssn(),
                "clientUid": random.randint(1, 1500),
                "clientContactUid": 1,
                "patientUid": random.randint(1, 210196),
                "priority": random.choice([0, 2]),
                "samples": [gen_sample() for _x in range(random.randint(1, 3))],
            }
        } for i in range(100)
    ] for x in range(25000)
]

# def do_work1(var_list):
#     auth_headers = authenticate()
#
#     for variables in var_list:
#         run_query(query=add_patient_query, variables=variables, headers=auth_headers)
#


def start_ar_reg():
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = (executor.submit(do_work, add_ar_query, variables)
                         for variables in ar_variables)

        for future in concurrent.futures.as_completed(future_to_url):
            try:
                data = future.result()
                logger.info("Done")
            except Exception as exc:
                logger.error(exc)
