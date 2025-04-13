from faker import Faker
import random

import logging
from metadata import fetch_clients

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

def get_patient(username: str):
    clients = fetch_clients(username)
    client = random.choice(clients)
    return {
        'clientPatientId': engine.ssn(),
        'firstName': engine.first_name(),
        'middleName': engine.first_name(),
        'lastName': engine.last_name(),
        'age': random.randint(1, 90),
        'gender': random.choice(["Male", "Female"]),
        'dateOfBirth': str(engine.date_time()),
        'ageDobEstimated': engine.boolean(),
        'clientUid': client["uid"],
        'phoneMobile': engine.phone_number(),
        'phoneHome': engine.phone_number(),
        'consentSms': engine.boolean(),
    }, client
