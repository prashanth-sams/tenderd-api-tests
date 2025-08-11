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
from tests.data.schema.update_equipment_status import _ok_schema, _err_schema
from tests.helpers.hooks import Api
from datetime import datetime, timezone

from requests.structures import CaseInsensitiveDict
from assertpy import assert_that
from cerberus import Validator


ALLOWED_STATUS = {"Active", "Idle", "Under Maintenance"}

def _unique_name(base: str) -> str:
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")[-6:]
    return f"{base} #{suffix}"

def _parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ============================================================
# POST /api/equipment/{id}/status suite
# ============================================================
@pytest.mark.smoke
class TestUpdateEquipmentStatus(Api):
    """
    @description: Test suite for validating POST /api/equipment/{id}/status
    """

    @pytest.fixture
    def get_headers(self, def_headers):
        return def_headers

    def _create_equipment(self, headers, *, name="Excavator CAT 320", status="Idle", location="Site A"):
        payload = {"name": _unique_name(name), "status": status, "location": location}
        self.log.info(f'Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {headers}\n\tpayload: {payload}')
        r = requests.post(f"{BASE_URI}/api/equipment", headers=headers, json=payload, verify=True)
        assert r.status_code == 201, f"Create failed ({r.status_code}): {r.text}"
        body = r.json()
        eq = body["data"]
        return eq  # dict with id, name, status, location, lastUpdated

    def _pick_new_status(self, current: str) -> str:
        order = ["Active", "Idle", "Under Maintenance"]
        if current not in order:
            return "Active"
        idx = order.index(current)
        return order[(idx + 1) % len(order)]

    def _get_equipment_list(self, headers):
        self.log.info(f'Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {headers}')
        r = requests.get(f"{BASE_URI}/api/equipment", headers=headers, verify=True)
        assert r.status_code == 200
        return r.json().get("data", [])

    @pytest.mark.status
    @pytest.mark.datavalidation
    def test_update_status(self, get_headers):
        """
        @description: Create an equipment, update its status, validate response & side effects.
        """
        ## Create equipment with known starting status
        created = self._create_equipment(get_headers, status="Idle")
        eq_id = created["id"]
        target_status = self._pick_new_status(created["status"])
        payload = {"status": target_status, "changedBy": "Operator John"}

        self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment/{eq_id}/status\n\theaders: {get_headers}\n\tpayload: {payload}")
        self.log.info(f"UPDATE status -> id={eq_id}, payload={payload} " f"({BASE_URI}/api/equipment/{eq_id}/status)")
        r = requests.post(
            f"{BASE_URI}/api/equipment/{eq_id}/status",
            headers=get_headers,
            json=payload,
            verify=True,
        )
        self.log.info(f"Response {r.status_code}: {r.text}")
        assert r.status_code == 200
        assert r.headers["Content-Type"].startswith("application/json")

        body = r.json()
        v = Validator(_ok_schema, require_all=True)
        assert v.validate(body), f"Schema errors: {v.errors}"

        # Envelope & entity checks
        equipment = body["data"]["equipment"]
        history = body["data"]["historyEntry"]

        assert equipment["id"] == eq_id
        assert history["equipmentId"] == eq_id

        # History consistency
        assert history["changedBy"] == "Operator John"
        assert history["newStatus"] == equipment["status"]
        assert history["previousStatus"] == created["status"]
        assert history["newStatus"] in ALLOWED_STATUS

        # Timestamps parseable
        _ = _parse_iso(equipment["lastUpdated"])
        _ = _parse_iso(history["timestamp"])

        # Eventually visible via GET /api/equipment
        found_status = None
        for _ in range(10):
            items = self._get_equipment_list(get_headers)
            for it in items:
                if it["id"] == eq_id:
                    found_status = it["status"]
                    break
            if found_status == equipment["status"]:
                break
            time.sleep(0.3)
        assert found_status == equipment["status"], "Updated status not reflected in listing"

    @pytest.mark.negative
    @pytest.mark.schema
    @pytest.mark.parametrize("bad_payload", [
        {"status": "BROKEN", "changedBy": "Operator John"},  # invalid status
        {"changedBy": "Operator John"},                      # missing status
    ])
    def test_update_status_400_bad_request(self, get_headers, bad_payload):
        """
        @description: Test updating status with invalid payload.
        """
        created = self._create_equipment(get_headers, status="Active")
        eq_id = created["id"]

        self.log.info(f'Request\n\turl: {BASE_URI}/api/equipment/{eq_id}/status\n\theaders: {get_headers}\n\tpayload: {bad_payload}')
        r = requests.post(
            f"{BASE_URI}/api/equipment/{eq_id}/status",
            headers=get_headers,
            json=bad_payload,
            verify=True,
        )
        self.log.info(f"400 attempt id={eq_id} payload={bad_payload} -> {r.status_code} {r.text}")

        assert r.status_code == 400
        assert r.headers["Content-Type"].startswith("application/json")

        v = Validator(_err_schema, require_all=True)
        assert v.validate(r.json()), f"Schema errors: {v.errors}"

    @pytest.mark.negative
    @pytest.mark.schema
    def test_update_status_404_equipment_not_found(self, get_headers):
        """
        @description: Test updating status for a non-existing equipment.
        """
        items = self._get_equipment_list(get_headers)
        max_id = max([it["id"] for it in items], default=0)
        missing_id = max_id + 99999

        payload = {"status": "Idle", "changedBy": "Operator John"}
        r = requests.post(
            f"{BASE_URI}/api/equipment/{missing_id}/status",
            headers=get_headers,
            json=payload,
            verify=True,
        )
        self.log.info(f"404 attempt id={missing_id} -> {r.status_code} {r.text}")

        assert r.status_code == 404
        assert r.headers["Content-Type"].startswith("application/json")

        v = Validator(_err_schema, require_all=True)
        assert v.validate(r.json()), f"Schema errors: {v.errors}"

    @pytest.mark.performance
    def test_update_status_response_time(self, get_headers):
        """
        @description: Measure the response time for updating equipment status.
        """
        created = self._create_equipment(get_headers, status="Active")
        eq_id = created["id"]
        payload = {"status": self._pick_new_status(created["status"]), "changedBy": "Operator John"}

        self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment/{eq_id}/status\n\theaders: {get_headers}\n\tpayload: {payload}")
        r = requests.post(
            f"{BASE_URI}/api/equipment/{eq_id}/status",
            headers=get_headers,
            json=payload,
            verify=True,
        )
        elapsed_ms = r.elapsed.total_seconds() * 1000
        self.log.info(f"UPDATE time: {elapsed_ms:.1f} ms (status={r.status_code})")
        assert elapsed_ms <= 500, f"Slow status update: {elapsed_ms:.1f} ms"
        assert r.status_code == 200
