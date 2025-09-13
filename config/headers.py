import os
from dotenv import load_dotenv

load_dotenv()


class Headers:

    @staticmethod
    def org_admin(
            customer_code: str = os.getenv("ADMIN_CUSTOMER_CODE"),
            api_key: str = os.getenv("ADMIN_API_KEY")
    ) -> dict:
        return {
            "X-Customer-Code": customer_code,
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        }

    @staticmethod
    def team_admin(
            customer_code: str = os.getenv("TEAM_ADMIN_CUSTOMER_CODE"),
            api_key: str = os.getenv("TEAM_ADMIN_API_KEY")
    ) -> dict:
        return {
            "X-Customer-Code": customer_code,
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        }

    @staticmethod
    def team_viewer(
            customer_code: str = os.getenv("TEAM_VIEWER_CUSTOMER_CODE"),
            api_key: str = os.getenv("TEAM_VIEWER_API_KEY")
    ) -> dict:
        return {
            "X-Customer-Code": customer_code,
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        }
