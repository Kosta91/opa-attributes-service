"""Mock responses for external attribute sources, keyed by principal_id."""

IDENTITY_ATTRIBUTES: dict[str, dict[str, str]] = {
    "alice": {
        "email": "alice@example.com",
        "name": "Alice Johnson",
        "oncall": "false",
    },
    "bob": {
        "email": "bob@example.com",
        "name": "Bob Smith",
        "oncall": "true",
    },
    "john": {
        "email": "john@example.com",
        "name": "John Doe",
        "oncall": "false",
    },
    "carol": {
        "email": "carol@example.com",
        "name": "Carol Williams",
        "oncall": "false",
    },
    "dave": {
        "email": "dave@example.com",
        "name": "Dave Brown",
        "oncall": "true",
    },
    "eve": {
        "email": "eve@example.com",
        "name": "Eve Davis",
        "oncall": "false",
    },
    "frank": {
        "email": "frank@example.com",
        "name": "Frank Miller",
        "oncall": "false",
    },
    "grace": {
        "email": "grace@example.com",
        "name": "Grace Wilson",
        "oncall": "true",
    },
    "hank": {
        "email": "hank@example.com",
        "name": "Hank Moore",
        "oncall": "false",
    },
    "iris": {
        "email": "iris@example.com",
        "name": "Iris Taylor",
        "oncall": "false",
    },
}

ORG_ATTRIBUTES: dict[str, dict[str, str]] = {
    "alice": {
        "department": "Vehicle Security",
        "jobTitle": "Security Engineer",
        "team": "VehicleSec",
        "location": "Foster City",
    },
    "bob": {
        "department": "ProdSec",
        "jobTitle": "Staff Security Engineer",
        "team": "ProdSec",
        "location": "Foster City",
    },
    "john": {
        "department": "ProdSec",
        "jobTitle": "Product Security Engineer",
        "team": "ProdSec",
        "location": "Bayside T1",
    },
    "carol": {
        "department": "Infrastructure",
        "jobTitle": "SRE Lead",
        "team": "Platform",
        "location": "Foster City",
    },
    "dave": {
        "department": "Infrastructure",
        "jobTitle": "DevOps Engineer",
        "team": "Platform",
        "location": "Seattle",
    },
    "eve": {
        "department": "Data Science",
        "jobTitle": "ML Engineer",
        "team": "Perception",
        "location": "Foster City",
    },
    "frank": {
        "department": "Vehicle Security",
        "jobTitle": "Firmware Engineer",
        "team": "VehicleSec",
        "location": "Bayside T1",
    },
    "grace": {
        "department": "ProdSec",
        "jobTitle": "AppSec Engineer",
        "team": "ProdSec",
        "location": "Seattle",
    },
    "hank": {
        "department": "Infrastructure",
        "jobTitle": "Network Engineer",
        "team": "NetOps",
        "location": "Bayside T1",
    },
    "iris": {
        "department": "Data Science",
        "jobTitle": "Data Analyst",
        "team": "Analytics",
        "location": "Foster City",
    },
}
