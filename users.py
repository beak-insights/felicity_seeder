import concurrent.futures
from faker import Faker
from core import do_work, run_query, authenticate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = Faker()

add_user_mutation = """
    mutation AddUser($firstName: String!, $lastName: String!, $email: String!, $groupUid: String, $userName: String!, $password: String!, $passwordc: String!) {
        createUser(firstName: $firstName, lastName: $lastName, email: $email, groupUid: $groupUid, userName: $userName, password: $password, passwordc: $passwordc) {
            ... on UserType {
                uid
                firstName
                lastName
                email
                mobilePhone
                userName
            }
            ... on OperationError {
                error
                suggestion
            }
        }
    }
"""

fetch_users_query = """ 
    query { userAll { items { userName } } }
"""

_unique = []

def user_faker():
    while True:
        first_name = engine.first_name()
        last_name = engine.last_name()
        if first_name not in _unique:
            _unique.append(first_name)
            break

    return {
        'firstName': first_name,
        'lastName': last_name,
        'email': f"{first_name}{last_name}@felcity.com".lower(),
        'userName': f"{last_name}{first_name[0]}".strip().lower(),
        'password': '@Access123!',
        'passwordc': '@Access123!',
        'groupUid': None,
    }

def fetch_existing_users():
    """Fetch all existing users from the system"""
    try:
        headers = authenticate({"username":"admin", "password": "!Felicity#100"})
        users_response = run_query(fetch_users_query, {}, headers)
        if users_response:
            return [user["userName"] for user in users_response["data"]["userAll"]["items"]]
        return []
    except Exception as exc:
        logger.error(f"Error fetching users: {exc}")
        return []


def create_users(num_users_needed):
    """Create the specified number of users"""
    fake_users = [user_faker() for _ in range(num_users_needed)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = executor.submit(do_work, add_user_mutation, fake_users, ["admin"])

        try:
            data = future_to_url.result()
            return [item["data"]["createUser"]["userName"] for item in data]
        except Exception as exc:
            logger.error(f"Error creating users: {exc}")
            return []

def init_users(total=10):
    """Initialize users - if not exists then create"""
    existing_users = fetch_existing_users()
    existing_count = len(existing_users)
    
    logger.info(f"Found {existing_count} existing users")
    
    if existing_count >= total:
        logger.info(f"At least {total} users already exist. No need to create more.")
        return existing_users
    
    # Calculate how many more users we need to create
    num_users_needed = total - existing_count
    logger.info(f"Creating {num_users_needed} additional users")
    
    # Create the required number of users
    new_users = create_users(num_users_needed)
    
    # Return combined list of existing and new users
    return existing_users + new_users

# Main execution
if __name__ == "__main__":
    init_users()