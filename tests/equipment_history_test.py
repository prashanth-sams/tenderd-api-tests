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
from tests.data.schema.equipment_history import _ok_schema, _err_schema
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

def _cycle_status(cur: str) -> str:
    order = ["Active", "Idle", "Under Maintenance"]
    i = order.index(cur) if cur in order else -1
    return order[(i + 1) % len(order)]


# ============================================================
# GET /api/equipment/{id}/history suite
# ============================================================
@pytest.mark.smoke
class TestGetEquipmentHistory(Api):
    @pytest.fixture
    def get_headers(self, def_headers):
        return def_headers

    def _create_equipment(self, headers, *, name="Excavator CAT 320", status="Active", location="Site A"):
        """
        @description: Create a new piece of equipment.
        """
        payload = {"name": _unique_name(name), "status": status, "location": location}
        self.log.info(f"CREATE equipment -> {payload}")
        self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment\n\theaders: {headers}\n\tbody: {payload}")
        r = requests.post(f"{BASE_URI}/api/equipment", headers=headers, json=payload, verify=True)
        assert r.status_code == 201, f"Create failed ({r.status_code}): {r.text}"
        self.log.info(f"Response {r.status_code}: {r.text}")
        return r.json()["data"]

    def _get_history(self, headers, eq_id: int, *, limit=None, offset=None):
        """
        @description: Fetch equipment history
        """
        params = {}
        if limit is not None: params["limit"] = limit
        if offset is not None: params["offset"] = offset
        self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment/{eq_id}/history\n\theaders: {headers}\n\tparams: {params}")
        url = f"{BASE_URI}/api/equipment/{eq_id}/history"
        self.log.info(f"GET history {url} params={params}")
        r = requests.get(url, headers=headers, params=params, verify=True)
        return r

    def _seed_history(self, headers, eq_id: int, start_status: str):
        """
        @description: Perform N transitions to ensure there is history to page over
        """
        cur = start_status
        actors = ["Operator John", "Technician Mike"]
        last_response = None
        for i in range(len(actors)):
            cur = _cycle_status(cur)
            self.log.info(f"Transitioning equipment {eq_id} from {cur} by {actors[i % len(actors)]}")

            payload = {"status": cur, "changedBy": actors[i % len(actors)]}
            self.log.info(f"Request\n\turl: {BASE_URI}/api/equipment/{eq_id}/status\n\theaders: {headers}\n\tbody: {payload}")
            r = requests.post(f"{BASE_URI}/api/equipment/{eq_id}/status", headers=headers, json=payload, verify=True)
            assert r.status_code == 200, f"Update failed ({r.status_code}): {r.text}"
            self.log.info(f"Status updated to {cur} by {actors[i % len(actors)]}")
            self.log.info(f"Response {r.status_code}: {r.text}")
            last_response = r.json()["data"]
        return last_response

    @pytest.mark.status
    @pytest.mark.schema
    @pytest.mark.datavalidation
    def test_equipment_history(self, get_headers):
        """
        @description: Test fetching equipment history with valid parameters
        """
        created = self._create_equipment(get_headers, status="Active")
        eq_id = created["id"]

        self._seed_history(get_headers, eq_id, created["status"])

        r = self._get_history(get_headers, eq_id, limit=5, offset=0)
        self.log.info(f"Response {r.status_code}: {r.text}")
        assert r.status_code == 200
        assert r.headers["Content-Type"].startswith("application/json")

        body = r.json()
        v = Validator(_ok_schema, require_all=True)
        assert v.validate(body), f"Schema errors: {v.errors}"

        data = body["data"]
        assert data["equipmentId"] == eq_id
        assert data["total"] >= len(data["history"]) >= 0
        assert data["limit"] == 5
        assert data["offset"] == 0
        assert data["hasMore"] == (data["total"] > data["offset"] + len(data["history"]))

        # Per-entry checks
        for h in data["history"]:
            assert h["equipmentId"] == eq_id
            assert h["previousStatus"] in ALLOWED_STATUS
            assert h["newStatus"] in ALLOWED_STATUS
            _ = _parse_iso(h["timestamp"])

    @pytest.mark.performance
    def test_history_response_time(self, get_headers):
        """
        @description: Measure the response time for fetching equipment history.
        """
        created = self._create_equipment(get_headers, status="Active")
        eq_id = created["id"]
        self._seed_history(get_headers, eq_id, created["status"])

        r = self._get_history(get_headers, eq_id, limit=5, offset=0)
        elapsed_ms = r.elapsed.total_seconds() * 1000
        self.log.info(f"HISTORY time: {elapsed_ms:.1f} ms (status={r.status_code})")
        assert r.status_code == 200
        assert elapsed_ms <= 500, f"Slow history retrieval: {elapsed_ms:.1f} ms"
