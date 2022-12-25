# from patients import start_patient_reg
# from analysis import start_ar_reg
from users import start_user_reg
from users import fetch_user_auths
from bundling import patient_plus_ar_reg


if __name__ == '__main__':
    print("Faking Felicity Data....... .....")

    # start_user_reg(['admin'])
    users_usernames = sorted(fetch_user_auths(['admin']))

    patient_plus_ar_reg(users_usernames[:12])

    # start_patient_reg(users_usernames)
    # start_ar_reg(users_usernames)
