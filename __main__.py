from datetime import datetime

from users import init_users
from bundling import patient_plus_ar_reg

if __name__ == '__main__':
    print("Faking Felicity Data....... .....")

    start_time = datetime.now()
    print(f"Start Time: {start_time.isoformat()}")

    usernames = init_users()
    usernames = list(filter(lambda un: un not in ["admin", "system_daemon"], usernames))

    patient_plus_ar_reg(usernames, 10000)

    end_time = datetime.now()
    print(f"End Time: {end_time.isoformat()}")

    duration = end_time - start_time
    print(f"Duration: {duration}")
