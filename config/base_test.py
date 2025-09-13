from services.licenses.api_licenses import LicensesApi
from config.headers import Headers

class BaseTest:

    def setup_method(self):
        self.api_licenses = LicensesApi()
        self.org_admin_headers = Headers.org_admin()
        self.team_admin_headers = Headers.team_admin()
        self.team_viewer_headers = Headers.team_viewer()
