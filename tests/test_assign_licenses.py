import copy
import threading

import allure
import pytest
from config.base_test import BaseTest
from services.licenses.payloads import Payloads
from services.licenses.models.assign_licenses_models import ErrorResponse
from config.constants import TEAM_1_ID, VALID_EMAIL_2


@allure.epic("Licenses API")
@allure.feature("Assign license")
class TestLicenses(BaseTest):

    @pytest.fixture
    def base_assign_license_payload(self):
        payload = Payloads.get_base_assign_license_payload()

        available_license_id = self.api_licenses.get_available_to_assign_team_license_id(
            headers=self.org_admin_headers, team_id=TEAM_1_ID)
        payload["licenseId"] = available_license_id

        return payload

    # -------------------------
    # Positive tests
    # -------------------------
    @allure.title("Assign by licenseId - success")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.positive
    def test_assign_by_license_id_success(self, base_assign_license_payload):
        with allure.step("Arrange: prepare payload with existing licenseId"):
            payload = copy.deepcopy(base_assign_license_payload)

        with allure.step("Act: call AssignLicense endpoint as org_admin"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: HTTP 200 and response body is empty (license assigned)"):
            assert response.status_code == 200
            assert not response.content

    @allure.title("Assign by team (productCode + team) - success")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.positive
    def test_assign_by_team_success(self, base_assign_license_payload):
        with allure.step("Arrange: switch to license object (productCode + team)"):
            payload = copy.deepcopy(base_assign_license_payload)
            del payload["licenseId"]
            product_code = self.api_licenses.get_available_to_assign_team_license_product_code(
                headers=self.org_admin_headers, team_id=TEAM_1_ID)
            payload["license"] = {"productCode": product_code, "team": TEAM_1_ID}

        with allure.step("Act: call AssignLicense endpoint using license object"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: HTTP 200 and no response content (assignment succeeded)"):
            assert response.status_code == 200
            assert not response.content

    @allure.title("When both licenseId and license are present, licenseId is used")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.positive
    def test_assign_uses_licenseid_when_both_fields_are_present(self, base_assign_license_payload):
        with allure.step("Arrange: payload contains both licenseId and license object"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload["license"] = {
                "productCode": self.api_licenses.get_available_to_assign_team_license_product_code(
                    headers=self.org_admin_headers, team_id=TEAM_1_ID),
                "team": TEAM_1_ID
            }

        with allure.step("Act: call AssignLicense endpoint"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: HTTP 200 (server used licenseId, not license object)"):
            assert response.status_code == 200

    @allure.title("Assign with includeOfflineActivationCode flag (True/False)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.positive
    @pytest.mark.parametrize("include_code", [True, False], ids=["With Offline Code", "Without Offline Code"])
    def test_assign_with_offline_activation_code_flag(self, base_assign_license_payload, include_code):
        with allure.step("Arrange: set includeOfflineActivationCode flag"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload["includeOfflineActivationCode"] = include_code

        with allure.step("Act: assign license with the flag"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: HTTP 200 (assignment successful)"):
            assert response.status_code == 200

    @allure.title("Team admin can assign license")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.roles
    def test_team_admin_can_assign(self, base_assign_license_payload):
        with allure.step("Arrange: prepare payload using valid licenseId"):
            payload = copy.deepcopy(base_assign_license_payload)

        with allure.step("Act: call AssignLicense as team_admin"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.team_admin_headers)

        with allure.step("Assert: HTTP 200 and empty body (team_admin is allowed)"):
            assert response.status_code == 200
            assert not response.content

    # -------------------------
    # Negative tests
    # -------------------------
    @allure.title("Fails if no license field provided")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_fails_if_no_license_field_is_provided(self, base_assign_license_payload):
        with allure.step("Arrange: remove licenseId and do not provide license object"):
            payload = copy.deepcopy(base_assign_license_payload)
            del payload["licenseId"]

        with allure.step("Act: call AssignLicense expecting validation error"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: HTTP 400 and error body matches ErrorResponse schema"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Fails if contact object missing")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_fails_if_contact_missing(self, base_assign_license_payload):
        with allure.step("Arrange: remove contact from payload"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload.pop("contact", None)

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: HTTP 400 and error schema"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Fails if contact.{email|firstName|lastName} missing")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.parametrize("missing_field", ["email", "firstName", "lastName"])
    def test_fails_if_contact_field_missing(self, base_assign_license_payload, missing_field):
        with allure.step(f"Arrange: remove contact.{missing_field} from payload"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload["contact"].pop(missing_field, None)

        with allure.step("Act: call API"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: validation error 400 and ErrorResponse schema"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Fails if neither licenseId nor license provided")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_fails_if_neither_licenseId_nor_license_provided(self, base_assign_license_payload):
        with allure.step("Arrange: remove licenseId (and keep no license block)"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload.pop("licenseId", None)

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Fails if license object missing productCode/team (parameterized)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.parametrize("missing_field", ["productCode", "team"])
    def test_fails_if_license_object_missing_product_or_team(self, base_assign_license_payload, missing_field):
        with allure.step("Arrange: build license object with missing field"):
            payload = copy.deepcopy(base_assign_license_payload)
            if "licenseId" in payload:
                del payload["licenseId"]

            if missing_field == "productCode":
                payload["license"] = {"team": TEAM_1_ID}
            else:
                payload["license"] = {"productCode": self.api_licenses.get_available_to_assign_team_license_product_code(
                    headers=self.org_admin_headers, team_id=TEAM_1_ID)}

        with allure.step("Act: call API expecting validation error"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 and ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Fails if sendEmail missing")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_fails_if_sendEmail_missing(self, base_assign_license_payload):
        with allure.step("Arrange: remove sendEmail from payload"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload.pop("sendEmail", None)

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Fails if includeOfflineActivationCode missing")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_fails_if_includeOfflineActivationCode_missing(self, base_assign_license_payload):
        with allure.step("Arrange: remove includeOfflineActivationCode from payload"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload.pop("includeOfflineActivationCode", None)

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("sendEmail wrong types (parametrized)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.parametrize("bad_value", ["true", 1, None, {}])
    def test_fails_if_sendEmail_wrong_type(self, base_assign_license_payload, bad_value):
        with allure.step(f"Arrange: set sendEmail to invalid type: {bad_value!r}"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload["sendEmail"] = bad_value

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("includeOfflineActivationCode wrong types (parametrized)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.parametrize("bad_value", ["false", 0, None, {}])
    def test_fails_if_includeOfflineActivationCode_wrong_type(self, base_assign_license_payload, bad_value):
        with allure.step(f"Arrange: set includeOfflineActivationCode to invalid type: {bad_value!r}"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload["includeOfflineActivationCode"] = bad_value

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("license.team invalid type / value (parametrized)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.parametrize("bad_team", ["1", 1.5, -5, None, {}])
    def test_fails_if_license_team_invalid_type_or_value(self, base_assign_license_payload, bad_team):
        with allure.step(f"Arrange: set license.team to invalid value: {bad_team!r}"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload.pop("licenseId", None)
            payload["license"] = {"productCode": self.api_licenses.get_available_to_assign_team_license_product_code(
                headers=self.org_admin_headers, team_id=TEAM_1_ID), "team": bad_team}

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Invalid email format")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_fails_if_email_invalid_format(self, base_assign_license_payload):
        with allure.step("Arrange: set invalid email format in payload"):
            payload = copy.deepcopy(base_assign_license_payload)
            payload["contact"]["email"] = "not-an-email"

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Empty or whitespace-only values (parametrized)")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.parametrize("field, value", [
        ("contact.email", ""),
        ("contact.firstName", ""),
        ("contact.lastName", "   "),
        ("licenseId", ""),
    ])
    def test_fails_on_empty_or_whitespace_values(self, base_assign_license_payload, field, value):
        with allure.step(f"Arrange: set {field} to {value!r}"):
            payload = copy.deepcopy(base_assign_license_payload)
            if field.startswith("contact."):
                _, sub = field.split(".")
                payload["contact"][sub] = value
            else:
                payload[field] = value

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 + ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Non-existent licenseId")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_fails_for_nonexistent_licenseId(self):
        with allure.step("Arrange: use payload without licenseId to trigger not-found handling"):
            payload = Payloads.get_base_assign_license_payload()

        with allure.step("Act"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)

        with allure.step("Assert: 400 and ErrorResponse"):
            assert response.status_code == 400
            ErrorResponse(**response.json())

    @allure.title("Assign already assigned license fails")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    def test_fails_when_license_already_assigned(self):
        with allure.step("Arrange: assign a license once to ensure it's taken"):
            first_payload = Payloads.get_base_assign_license_payload()
            available_license_id = self.api_licenses.get_available_to_assign_team_license_id(
                headers=self.org_admin_headers, team_id=TEAM_1_ID)
            first_payload["licenseId"] = available_license_id

            first_response = self.api_licenses.assign_license(payload=first_payload, headers=self.org_admin_headers)
            assert first_response.status_code == 200

        with allure.step("Act: try to assign the same license to another user"):
            second_payload = Payloads.get_base_assign_license_payload()
            second_payload["licenseId"] = available_license_id
            second_payload["contact"]["email"] = VALID_EMAIL_2

            second_response = self.api_licenses.assign_license(payload=second_payload, headers=self.org_admin_headers)

        with allure.step("Assert: second assignment fails with 400 and proper error schema"):
            assert second_response.status_code == 400
            ErrorResponse(**second_response.json())

    @allure.title("Concurrent assignment: one succeeds, other fails")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_concurrent_assignment_one_succeeds_other_fails(self):
        with allure.step("Arrange: get a free licenseId and prepare two payloads"):
            license_id = self.api_licenses.get_available_to_assign_team_license_id(
                headers=self.org_admin_headers, team_id=TEAM_1_ID)
            p1 = Payloads.get_base_assign_license_payload()
            p1["licenseId"] = license_id
            p2 = Payloads.get_base_assign_license_payload()
            p2["licenseId"] = license_id
            p2["contact"]["email"] = VALID_EMAIL_2

        with allure.step("Act: send two requests in parallel"):
            results = []

            def thread_call(payload):
                resp = self.api_licenses.assign_license(payload=payload, headers=self.org_admin_headers)
                results.append(resp)

            t1 = threading.Thread(target=thread_call, args=(p1,))
            t2 = threading.Thread(target=thread_call, args=(p2,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

        with allure.step("Assert: exactly one request succeeded (200) and one failed (400)"):
            assert len(results) == 2
            status_codes = sorted([r.status_code for r in results])
            assert status_codes == [200, 400]
            for r in results:
                if r.status_code == 400:
                    ErrorResponse(**r.json())

    @allure.title("Team member must NOT be able to assign license (RBAC)")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.roles
    def test_team_member_cannot_assign(self, base_assign_license_payload):
        with allure.step("Arrange: prepare payload and identify team_viewer headers"):
            payload = copy.deepcopy(base_assign_license_payload)

        with allure.step("Act: attempt to assign license as team_viewer (unauthorized)"):
            response = self.api_licenses.assign_license(payload=payload, headers=self.team_viewer_headers)

        with allure.step("Assert: RBAC denies action — expected 403 and error schema"):
            assert response.status_code == 403
            ErrorResponse(**response.json())
