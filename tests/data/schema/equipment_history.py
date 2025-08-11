ALLOWED_STATUS = {"Active", "Idle", "Under Maintenance"}

_ok_schema = {
    "success": {"type": "boolean", "allowed": [True], "required": True},
    "data": {
        "type": "dict",
        "required": True,
        "nullable": False,
        "allow_unknown": False,
        "schema": {
            "equipmentId": {"type": "integer", "required": True},
            "history": {
                "type": "list",
                "required": True,
                "minlength": 0,
                "schema": {
                    "type": "dict",
                    "allow_unknown": False,
                    "schema": {
                        "id": {"type": "integer", "required": True},
                        "equipmentId": {"type": "integer", "required": True},
                        "previousStatus": {
                            "type": "string",
                            "allowed": ["Active", "Idle", "Under Maintenance"],
                            "required": True,
                        },
                        "newStatus": {
                            "type": "string",
                            "allowed": ["Active", "Idle", "Under Maintenance"],
                            "required": True,
                        },
                        "timestamp": {
                            "type": "string",
                                "regex": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?(?:Z|[+-]\d{2}:\d{2})$",
                            "required": True,
                        },
                        "changedBy": {"type": "string", "minlength": 1, "required": True},
                    },
                },
            },
            "total": {"type": "integer", "min": 0, "required": True},
            "limit": {"type": "integer", "min": 0, "required": True},
            "offset": {"type": "integer", "min": 0, "required": True},
            "hasMore": {"type": "boolean", "required": True},
        },
    },
}

_err_schema = {
    "success": {"type": "boolean", "allowed": [False], "required": True},
    "error": {"type": "string", "required": True},
}