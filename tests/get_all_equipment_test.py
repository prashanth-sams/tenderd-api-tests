"""
@Author:       Prashanth Sams
@Created:      Fri Aug  10 22:55:27 2025 (-0400)
"""
import json
from datetime import datetime, timezone

import pytest
import requests
from assertpy import assert_that
from cerberus import Validator
import jsonpath as jp

from config import BASE_URI
from tests.data.schema.get_all_equipment import _ok_schema
from tests.helpers.hooks import Api


# ============================================================
# GET /api/equipment suite
# ============================================================
@pytest.mark.smoke
class TestGetAllEquipment(Api):
    """
    Test suite for validating GET /api/equipment responses
    """
    
    @pytest.fixture
    def get_headers(self, def_headers):
        """
        Get headers for the request
        """
        return def_headers

    @pytest.mark.status
    def test_get_all_equipment_status(self, get_headers):
        """
        @description: Test status code for GET /api/equipment
        """
        self.log.info(f'Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {get_headers}')
        r = requests.get(f'{BASE_URI}/api/equipment', headers=get_headers, verify=True)
        body = json.loads(r.text)
        self.log.info(f'Response\n\t{body}')
        
        ## Validate response code & headers
        assert r.status_code == 200
        assert r.headers['Content-Type'] == 'application/json'
        
        ## Envelope checks
        assert "success" in body and body["success"] is True
        assert body["count"] == len(body["data"])
        assert jp.jsonpath(body, '$.success')[0] is True

    @pytest.mark.negative
    def test_get_all_equipment_url_not_found(self, get_headers):
        """
        @description: Test status code for GET /api/equipment/234
        """
        self.log.info(f'Request\n\turl: {BASE_URI}/api/equipment/234\n\theaders: {get_headers}')
        r = requests.get(f"{BASE_URI}/api/equipment/234", headers=get_headers, verify=True)
        assert r.status_code == 404

    @pytest.mark.datavalidation
    def test_get_all_equipment_data_validation(self, get_headers):
        """
        @description: Test data validation for GET /api/equipment
        """
        self.log.info(f'Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {get_headers}')
        r = requests.get(f"{BASE_URI}/api/equipment", headers=get_headers, verify=True)
        body = json.loads(r.text)
        self.log.info(f'Response\n\t{body}')
        items = body.get("data", [])

        ## IDs unique
        ids = [it["id"] for it in items] 
        assert len(ids) == len(set(ids)), "Duplicate IDs found"

        ## Count matches
        assert body["count"] == len(items)

        ## Field-level checks
        ALLOWED_STATUS = {"Active", "Idle", "Under Maintenance"}

        for it in items:
            assert it["status"] in ALLOWED_STATUS, f"Bad status for id={it['id']}"
            assert isinstance(it["location"], str) and it["location"].strip() != ""
            
            ## Datetime format & not future
            dt = datetime.fromisoformat(it["lastUpdated"].replace("Z", "+00:00"))
            assert dt.tzinfo is not None
            assert dt <= datetime.now(timezone.utc) + (0 * (dt - dt)), "lastUpdated is in the future?"

    @pytest.mark.schema
    def test_get_all_equipment_schema(self, get_headers):
        """
        @description: Test schema validation for GET /api/equipment
        """
        self.log.info(f'Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {get_headers}')
        r = requests.get(f"{BASE_URI}/api/equipment", headers=get_headers, verify=True)
        body = json.loads(r.text)
        self.log.info(f'Response\n\t{body}')

        ## Validate response schema
        validator = Validator(_ok_schema, require_all=True)
        is_valid = validator.validate(body)
        assert_that(is_valid, description=validator.errors).is_true()

    @pytest.mark.performance
    def test_equipment_response_time(self, get_headers):
        """
        @description: Test performance for GET /api/equipment
        """
        self.log.info(f'Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {get_headers}')
        r = requests.get(f"{BASE_URI}/api/equipment", headers=get_headers, verify=True)
        elapsed_ms = r.elapsed.total_seconds() * 1000
        self.log.info(f'Response time: {elapsed_ms:.1f} ms')

        ## Performance check
        assert elapsed_ms <= 500, f"Slow response: {elapsed_ms:.1f} ms"
