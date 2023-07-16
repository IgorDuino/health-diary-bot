from garminconnect import Garmin


def check_garmin_credentials(garmin_username, garmin_password):
    try:
        gc = Garmin(garmin_username, garmin_password)
        gc.login()
        return True
    except Exception:
        return False
