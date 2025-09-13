from config.constants import BASE_URL


class Endpoints:

    assign_licenses = f"{BASE_URL}/customer/licenses/assign"
    get_team_licenses = lambda self, team_id: f"{BASE_URL}/customer/teams/{team_id}/licenses"
    change_licenses_team = f"{BASE_URL}/customer/changeLicensesTeam"