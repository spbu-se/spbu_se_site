# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Tests for /api/healthz endpoint."""

import json


class TestHealthz:
    def test_healthz_returns_200(self, client):
        resp = client.get("/api/healthz")
        assert resp.status_code == 200

    def test_healthz_returns_json(self, client):
        resp = client.get("/api/healthz")
        data = json.loads(resp.data)
        assert "status" in data
        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_healthz_no_auth_required(self, seeded_client):
        """Anonymous users can access healthz."""
        resp = seeded_client.get("/api/healthz")
        assert resp.status_code == 200
