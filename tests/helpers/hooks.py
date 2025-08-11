"""
@Author:       Prashanth Sams
@Created:      Fri Aug  10 22:55:27 2025 (-0400)
"""
import pytest
from requests.structures import CaseInsensitiveDict

class Api:
    """
    @Description: This method will be called before each test method runs
    """

    @pytest.fixture(autouse=True)
    def setup(self, logger, payload):
        """
        @Description: This method will be called before each test method runs
        """
        self.log = logger
        self.payload = payload
        yield
        self.log.info("End of test")
    
    @pytest.fixture
    def def_headers(self):
        """
        @Description: Set default headers for API requests
        """
        headers = CaseInsensitiveDict()
        headers["Accept"] = "*/*"
        headers["Content-Type"] = "application/json"
        headers["x-api-key"] = "reqres-free-v1"
        yield headers
    
    @pytest.fixture
    def base_payloads(self):
        """
        @Description: Set base payloads for creating equipment
        """
        return [
            {"name": "Excavator CAT 320",       "status": "Active",             "location": "Site A"},
            {"name": "Bulldozer Komatsu D65",   "status": "Idle",               "location": "Site B"},
            {"name": "Crane Liebherr LTM 1055", "status": "Under Maintenance",  "location": "Site C"},
        ]