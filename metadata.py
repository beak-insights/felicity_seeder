from core import run_query, authenticate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fetch_clients_query = """ 
    query { clientAll { items { uid name contacts { uid } } } }
"""

fetch_sample_types_query = """
    query { sampleTypeAll { uid name }}
"""

fetch_profiles_analyses_query = """
    query { profileAll {  uid name  } analysisAll { items { uid name} }}
"""

fetch_lab_instruments_query = """
    query { laboratoryInstrumentAll { items { uid labName instrument { uid name }} }}
"""

fetch_methods_query = """
    query { methodAll { items { uid name} }}
"""

def _fetch_metatada(query:str, username: str, variabes: dict ={}):
    """Fetch all fetch_clients from the system"""
    try:
        headers = authenticate({
            "username": username, 
            "password": "!Felicity#100" if username == 'admin' else "@Access123!"
        })
        response = run_query(query, variabes, headers)
        if response:
            return response["data"]
        return []
    except Exception as exc:
        logger.error(f"Error fetching clients: {exc}")
        return []

def fetch_clients(username: str):
    meta = _fetch_metatada(fetch_clients_query, username)
    return meta["clientAll"]["items"] if meta else []

def fetch_sample_types(username: str):
    meta = _fetch_metatada(fetch_sample_types_query, username)
    return [cl["uid"] for cl in meta["sampleTypeAll"]] if meta else []

def fetch_profiles_analyses(username: str):
    meta = _fetch_metatada(fetch_profiles_analyses_query, username)
    if not meta:
        return []
    profiles = [cl["uid"] for cl in meta["profileAll"]]
    analyses = [cl["uid"] for cl in meta["analysisAll"]["items"]]  
    return profiles, analyses

def fetch_lab_instruments(username: str):
    meta = _fetch_metatada(fetch_lab_instruments_query, username)
    return [cl["uid"] for cl in meta["laboratoryInstrumentAll"]["items"]] if meta else []

def fetch_methods(username: str):
    meta = _fetch_metatada(fetch_methods_query, username)
    return [cl["uid"] for cl in meta["methodAll"]["items"]] if meta else []

if __name__ == "__main__":
    fetch_clients("admin")
    fetch_sample_types("admin")
    fetch_profiles_analyses("admin")
    fetch_lab_instruments("admin")
    fetch_methods("admin")
