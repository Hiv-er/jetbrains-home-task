import allure
import requests

from services.licenses.endpoints import Endpoints
from utils.api_client import ApiClient


class LicensesApi(ApiClient):

    def __init__(self):
        self.endpoints = Endpoints()

    @allure.step("Assign license to a user")
    def assign_license(self, headers: dict, payload: dict) -> requests.Response:
        return self.post(self.endpoints.assign_licenses, headers=headers, payload=payload)

    @allure.step("Get licenses for the team_id={team_id}")
    def get_team_licenses(self, headers: dict, team_id: int) -> requests.Response:
        return self.get(url=self.endpoints.get_team_licenses(team_id), headers=headers)

    @allure.step("Find available to assign license for the team_id={team_id}")
    def get_available_to_assign_team_license_dict(self, headers: dict, team_id: int) -> dict:
        response = self.get_team_licenses(headers=headers, team_id=team_id)
        assert response.status_code == 200
        for license_obj in response.json():
            if license_obj["isAvailableToAssign"]:
                return license_obj

        raise AssertionError(f"No available licenses to assign for team_id={team_id}")

    @allure.step("Get available to assign license id for the team_id={team_id}")
    def get_available_to_assign_team_license_id(self, headers: dict, team_id: int) -> str:
        return self.get_available_to_assign_team_license_dict(headers=headers, team_id=team_id)["licenseId"]

    @allure.step("Get available to assign product code for the team_id={team_id}")
    def get_available_to_assign_team_license_product_code(self, headers: dict, team_id: int) -> str:
        return self.get_available_to_assign_team_license_dict(headers=headers, team_id=team_id)["product"]["code"]

    @allure.step("Change team for licenses")
    def change_licenses_team(self, headers: dict, payload: dict) -> requests.Response:
        return self.post(self.endpoints.change_licenses_team, headers=headers, payload=payload)
