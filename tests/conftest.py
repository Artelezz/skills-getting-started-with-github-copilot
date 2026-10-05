from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Practice chess strategies",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 3,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore painting and drawing",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 5,
        "participants": [],
    },
}


@pytest.fixture(autouse=True)
def activity_data(monkeypatch):
    isolated_activities = deepcopy(INITIAL_ACTIVITIES)
    monkeypatch.setattr(app_module, "activities", isolated_activities)
    return isolated_activities


@pytest.fixture
def client(activity_data):
    with TestClient(app_module.app) as test_client:
        yield test_client