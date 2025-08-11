"""
@Author:       Prashanth Sams
@Created:      Fri Aug  10 22:55:27 2025 (-0400)
"""
import json
import uuid
import pytest
import requests
import time
import jsonpath as jp

from jsonpath_ng import parse as rw_parse
from config import BASE_URI
from tests.data.schema.create_new_equipment import _ok_schema, _err_schema
from tests.helpers.hooks import Api
from datetime import datetime, timezone

from requests.structures import CaseInsensitiveDict
from assertpy import assert_that
from cerberus import Validator


ALLOWED_STATUS = {"Active", "Idle", "Under Maintenance"}

def _unique_name(base: str) -> str:
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")[-6:]
    return f"{base} #{suffix}"


# ============================================================
# POST /api/equipment suite
# ============================================================
@pytest.mark.smoke
class TestCreateNewEquipment(Api):
    """
    Test suite for validating POST /api/equipment responses
    """

    @pytest.fixture
    def get_headers(self, def_headers):
        """
        @description: Get headers for POST requests
        """
        return def_headers

    @pytest.mark.status
    @pytest.mark.datavalidation
    @pytest.mark.parametrize("idx", [0, 1, 2])
    def test_create_equipment_status_and_body(self, get_headers, base_payloads, idx):
        """
        @description: Test creating new equipment with valid status and body
        """
        base = base_payloads[idx]
        payload = dict(base)
        payload["name"] = _unique_name(base["name"])

        self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {get_headers}\n\tpayload: {payload}")
        r = requests.post(
            f"{BASE_URI}/api/equipment",
            headers=get_headers,
            json=payload,
            verify=True,
        )
        body = r.json()
        self.log.info(f"Response\n\t{body}")

        assert r.status_code == 201, f"Unexpected status: {r.status_code}"
        assert r.headers["Content-Type"].startswith("application/json")

        ## Envelope checks
        assert "success" in body and body["success"] is True
        assert "data" in body and isinstance(body["data"], dict)

        item = body["data"]
        for key in ("id", "name", "status", "location"):
            assert key in item, f"Missing key '{key}' in POST response"

        assert item["name"].startswith(base["name"])
        assert item["status"] in ALLOWED_STATUS
        assert isinstance(item["id"], int)

        created_id = item["id"]
        found = False
        for _ in range(10):  # Retry up to 10 times
            get_r = requests.get(f"{BASE_URI}/api/equipment", headers=get_headers, verify=True)
            get_body = get_r.json()
            created_ids = [i["id"] for i in get_body.get("data", [])]
            if created_id in created_ids:
                found = True
                break
            time.sleep(0.5)  # Wait 0.5 seconds before retrying
        assert found, "Created equipment not found via GET"

    @pytest.mark.schema
    def test_create_equipment_schema(self, get_headers):
        """
        @description: Validate response schema for POST /api/equipment
        """
        payload = {
            "name": _unique_name("Loader JCB 3DX"),
            "status": "Active",
            "location": "Site D",
        }
        self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {get_headers}\n\tpayload: {payload}")
        r = requests.post(f"{BASE_URI}/api/equipment", headers=get_headers, json=payload, verify=True)
        body = r.json()
        self.log.info(f"Response\n\t{body}")

        ## Validate response schema
        v = Validator(_ok_schema, require_all=True)
        assert v.validate(body), f"Schema errors: {v.errors}"
    
    @pytest.mark.schema
    @pytest.mark.negative
    @pytest.mark.parametrize("payload", [
        # Bad status -> 400
        {"name": "Backhoe", "status": "BROKEN", "location": "Site X"},
        # Missing name -> 400
        {"status": "Active", "location": "Site Y"},
    ])
    def test_create_equipment_validation_error(self, get_headers, payload):
        """
        @description: Test creating new equipment with invalid payload
        """
        # Make names unique when present
        if "name" in payload and payload["name"]:
            payload = dict(payload, name=_unique_name(payload["name"]))

        self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {get_headers}\n\tpayload: {payload}")
        r = requests.post(f"{BASE_URI}/api/equipment", headers=get_headers, json=payload, verify=True)
        self.log.info(f"POST 400 payload={payload} status={r.status_code} body={r.text}")

        assert r.status_code == 400
        assert r.headers["Content-Type"].startswith("application/json")

        body = r.json()
        v = Validator(_err_schema, require_all=True)
        assert v.validate(body), f"Schema errors: {v.errors}"

    @pytest.mark.datadriven
    def test_bulk_create_equipment_then_count_increases(self, get_headers, base_payloads):
        """
        @description: Create multiple items and assert count increases accordingly
        """
        self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {get_headers}")
        start_r = requests.get(f"{BASE_URI}/api/equipment", headers=get_headers, verify=True)
        start_body = start_r.json()
        start_count = start_body.get("count", len(start_body.get("data", [])))

        created = []
        for base in base_payloads:
            payload = dict(base)
            payload["name"] = _unique_name(base["name"])
            r = requests.post(f"{BASE_URI}/api/equipment", headers=get_headers, json=payload, verify=True)
            self.log.info(f"POST payload: {payload} -> status {r.status_code}")

            assert r.status_code == 201, f"Unexpected status: {r.status_code}"
            created.append(r.json()["data"]["id"])

        end_r = requests.get(f"{BASE_URI}/api/equipment", headers=get_headers, verify=True)
        end_body = end_r.json()
        end_count = end_body.get("count", len(end_body.get("data", [])))

        assert end_count >= start_count + len(created), (
            f"Count didn't increase as expected: start={start_count}, end={end_count}, created={len(created)}"
        )

        end_ids = [i["id"] for i in end_body.get("data", [])]
        for cid in created:
            assert cid in end_ids, f"Created id {cid} not found in listing"

    @pytest.mark.performance
    def test_create_equipment_response_time(self, get_headers):
        """
        @description: Test performance for POST /api/equipment
        """
        payload = {"name": _unique_name("Skid Steer S70"), "status": "Idle", "location": "Site Z"}
        self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {get_headers}\n\tpayload: {payload}")
        r = requests.post(f"{BASE_URI}/api/equipment", headers=get_headers, json=payload, verify=True)
        elapsed_ms = r.elapsed.total_seconds() * 1000
        self.log.info(f"POST time: {elapsed_ms:.1f} ms, status={r.status_code}")

        assert elapsed_ms <= 700, f"Slow POST: {elapsed_ms:.1f} ms"
        