import random
import string


def generate_license_code():
    letters_and_digits = string.ascii_uppercase + string.digits
    license_plate = ''.join(random.choice(letters_and_digits) for _ in range(9))
    return license_plate
