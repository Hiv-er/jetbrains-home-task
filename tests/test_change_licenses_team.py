import copy
import threading

import allure
import pytest
from config.constants import TEAM_1_ID, TEAM_2_ID
from services.licenses.models.assign_licenses_models import ErrorResponse
from config.base_test import BaseTest


@allure.epic("Licenses API")
@allure.feature("Change Licenses Team")
class TestChangeLicensesTeam(BaseTest):

    @pytest.fixture
    def base_change_team_payload(self):
        license_id = self.api_licenses.get_available_to_assign_team_license_id(
            headers=self.org_admin_headers,
            team_id=TEAM_1_ID
        )
        payload = {
            "licenseIds": [license_id],
            "targetTeamId": TEAM_2_ID
        }
        return payload

    # -------------------------
    # Positive tests
    # -------------------------
    @allure.title("Successfully change team for a single license")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_change_team_single_license_success(self, base_change_team_payload):
        with allure.step("Arrange: prepare payload"):
            payload = copy.deepcopy(base_change_team_payload)

        with allure.step("Act: call API to change license team"):
            response = self.api_licenses.change_licenses_team(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: validate successful response"):
            assert response.status_code == 200

    @allure.title("Successfully change team for multiple licenses")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_change_team_multiple_licenses_success(self):
        license_ids = [
            self.api_licenses.get_available_to_assign_team_license_id(
                headers=self.org_admin_headers,
                team_id=TEAM_1_ID
            ),
            self.api_licenses.get_available_to_assign_team_license_id(
                headers=self.org_admin_headers,
                team_id=TEAM_1_ID
            )
        ]
        payload = {"licenseIds": license_ids, "targetTeamId": TEAM_2_ID}

        with allure.step("Act: call API to change licenses team"):
            response = self.api_licenses.change_licenses_team(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: validate successful response"):
            assert response.status_code == 200

    # -------------------------
    # Negative tests
    # -------------------------
    @allure.title("Fail when licenseIds missing")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fails_when_licenseIds_missing(self):
        with allure.step("Arrange: prepare payload"):
            payload = {"targetTeamId": TEAM_2_ID}

        with allure.step("Act: call API with missing licenseIds"):
            response = self.api_licenses.change_licenses_team(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + validate error response"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Fail when targetTeamId missing")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fails_when_targetTeamId_missing(self):
        with allure.step("Arrange: prepare payload"):
            license_id = self.api_licenses.get_available_to_assign_team_license_id(
                headers=self.org_admin_headers,
                team_id=TEAM_1_ID
            )
            payload = {"licenseIds": [license_id]}
        with allure.step("Act: call API with missing targetTeamId"):
            response = self.api_licenses.change_licenses_team(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + validate error response"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Fail when licenseIds empty")
    @allure.severity(allure.severity_level.NORMAL)
    def test_fails_when_licenseIds_empty(self):
        with allure.step("Arrange: prepare payload"):
            payload = {"licenseIds": [], "targetTeamId": TEAM_2_ID}
        with allure.step("Act: call API with empty licenseIds"):
            response = self.api_licenses.change_licenses_team(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + validate error response"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Fail when team admin user tries to change licenses team")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_fails_when_team_admin(self, base_change_team_payload):
        with allure.step("Arrange: prepare payload"):
            payload = copy.deepcopy(base_change_team_payload)

        with allure.step("Act: call API with unauthorized headers"):
            response = self.api_licenses.change_licenses_team(payload=payload, headers=self.team_admin_headers)

        with allure.step("Assert: 403 + validate error response"):
            assert response.status_code == 403
            ErrorResponse(**response.json())

    @allure.title("Fail when team viewer user tries to change licenses team")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_fails_when_team_viewer(self, base_change_team_payload):
        with allure.step("Arrange: prepare payload"):
            payload = copy.deepcopy(base_change_team_payload)

        with allure.step("Act: call API with unauthorized headers"):
            response = self.api_licenses.change_licenses_team(payload=payload, headers=self.team_viewer_headers)

        with allure.step("Assert: 403 + validate error response"):
            assert response.status_code == 403
            ErrorResponse(**response.json())

    @allure.title("Concurrent transfer: one succeeds, other fails if licenses overlap")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_concurrent_transfer(self):
        with allure.step("Arrange: get a free licenseId and prepare two payloads"):
            license_id = self.api_licenses.get_available_to_assign_team_license_id(
                headers=self.org_admin_headers,
                team_id=TEAM_1_ID
            )

            p1 = {"licenseIds": [license_id], "targetTeamId": TEAM_2_ID}
            p2 = {"licenseIds": [license_id], "targetTeamId": TEAM_2_ID}

        with allure.step("Act: send two requests in parallel"):
            results = []

            def thread_call(payload):
                resp = self.api_licenses.change_licenses_team(payload=payload, headers=self.org_admin_headers)
                results.append(resp)

            t1 = threading.Thread(target=thread_call, args=(p1,))
            t2 = threading.Thread(target=thread_call, args=(p2,))

            t1.start()
            t2.start()
            t1.join()
            t2.join()

        with allure.step("Assert: one response 200, other 400"):
            status_codes = sorted([r.status_code for r in results])
            assert status_codes == [200, 400]

            for r in results:
                if r.status_code == 400:
                    ErrorResponse(**r.json())
