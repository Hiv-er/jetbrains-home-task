from faker import Faker
from config.constants import VALID_EMAIL_1

fake = Faker()


class Payloads:

    @staticmethod
    def get_base_assign_license_payload() -> dict:
        return {
            "contact": {
                "email": VALID_EMAIL_1,
                "firstName": fake.first_name(),
                "lastName": fake.last_name()
            },
            "includeOfflineActivationCode": False,
            "sendEmail": False,
            "licenseId": f"TEST-{fake.license_plate()}"
        }

