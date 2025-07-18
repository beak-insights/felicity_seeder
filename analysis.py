from datetime import datetime, timedelta
from faker import Faker
import random

import logging
from metadata import fetch_profiles_analyses, fetch_sample_types

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

# Define the time boundaries
now = datetime.now()
two_hours_ago = now - timedelta(hours=2)
one_week_ago = now - timedelta(weeks=1)

# Generate a random datetime between one_week_ago and two_hours_ago
def random_date_collected(start, end):
    start_ts = start.timestamp()
    end_ts = end.timestamp()
    random_ts = random.uniform(start_ts, end_ts)
    random_datetime = datetime.fromtimestamp(random_ts)
    return random_datetime


def gen_ar_request(username: str):
    sample_types = fetch_sample_types(username)
    profiles, analyses = fetch_profiles_analyses(username)
    _select_profiles = [random.choice(profiles) for _ in range(2)]
    _select_analyses = [random.choice(analyses) for _ in range(1 if _select_profiles else 4)]
    
    dc = random_date_collected(one_week_ago, two_hours_ago)
    dr = random_date_collected(dc, now)
    return {
        "sampleType": random.choice(sample_types),
        "profiles": _select_profiles,
        "analyses": _select_analyses,
        "dateCollected": dc.isoformat(),
        "dateReceived": dr.isoformat(),
    }

if __name__ == "__main__":
    gen_ar_request("admin")
