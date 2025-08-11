ALLOWED_STATUS = {"Active", "Idle", "Under Maintenance"}

_ok_schema = {
    "success": {"type": "boolean"},
    "data": {
        "type": "dict",
        "schema": {
            "id": {"type": "integer"},
            "name": {"type": "string", "minlength": 1},
            "status": {"type": "string", "allowed": list(ALLOWED_STATUS)},
            "location": {"type": "string", "minlength": 1},
            "lastUpdated": {"type": "string", "nullable": True, "required": False},
        },
    },
}

_err_schema = {
    "success": {"type": "boolean", "allowed": [False], "required": True},
    "error": {"type": "string", "required": True},
}