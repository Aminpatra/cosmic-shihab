"""Shared test setup: a fresh database per test and a clock the tests can move."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server  # noqa: E402


class Clock:
    def __init__(self):
        self.t = 1_800_000_000.0  # a fixed moment, so lease times are predictable

    def __call__(self):
        return self.t

    def advance(self, minutes):
        self.t += minutes * 60


@pytest.fixture
def clock(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "DB_PATH", str(tmp_path / "coordinator.db"))
    fake = Clock()
    monkeypatch.setattr(server, "now", fake)
    return fake
