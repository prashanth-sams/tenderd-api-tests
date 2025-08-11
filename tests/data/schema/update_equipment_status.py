ALLOWED_STATUS = {"Active", "Idle", "Under Maintenance"}

_ok_schema = {
    "success": {"type": "boolean", "allowed": [True]},
    "data": {
        "type": "dict",
        "schema": {
            "equipment": {
                "type": "dict",
                "schema": {
                    "id": {"type": "integer"},
                    "name": {"type": "string", "minlength": 1},
                    "status": {"type": "string", "allowed": list(ALLOWED_STATUS)},
                    "location": {"type": "string", "minlength": 1},
                    "lastUpdated": {"type": "string", "minlength": 1},
                },
            },
            "historyEntry": {
                "type": "dict",
                "schema": {
                    "id": {"type": "integer"},
                    "equipmentId": {"type": "integer"},
                    "previousStatus": {"type": "string", "allowed": list(ALLOWED_STATUS)},
                    "newStatus": {"type": "string", "allowed": list(ALLOWED_STATUS)},
                    "timestamp": {"type": "string", "minlength": 1},
                    "changedBy": {"type": "string", "minlength": 1},
                },
            },
        },
    },
}

_err_schema = {
    "success": {"type": "boolean", "allowed": [False], "required": True},
    "error": {"type": "string", "required": True},
}