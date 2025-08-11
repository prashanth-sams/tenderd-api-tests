
_ok_schema = {
    "success": {"type": "boolean", "required": True},
    "count": {"type": "integer", "min": 0, "required": True},
    "data": {
        "type": "list",
        "required": True,
        "schema": {
            "type": "dict",
            "allow_unknown": False,
            "schema": {
                "id": {"type": "integer", "min": 1, "required": True},
                "name": {"type": "string", "required": True},
                "status": {
                    "type": "string",
                    "allowed": ["Active", "Idle", "Under Maintenance"],
                    "required": True,
                },
                "location": {"type": "string", "required": True},
                "lastUpdated": {
                    "type": "string",
                    "regex": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$",
                    "required": True,
                },
            },
        },
    },
}
