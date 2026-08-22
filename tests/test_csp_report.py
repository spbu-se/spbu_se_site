# SPDX-License-Identifier: Apache-2.0

import json


class TestCspReport:
    def test_valid_report_returns_204(self, seeded_client):
        payload = {
            "csp-report": {
                "document-uri": "https://se.math.spbu.ru/",
                "blocked-uri": "https://evil.example.com/script.js",
                "violated-directive": "script-src 'self'",
            }
        }
        resp = seeded_client.post(
            "/csp-report",
            data=json.dumps(payload),
            content_type="application/csp-report",
        )
        assert resp.status_code == 204

    def test_valid_report_json_content_type_returns_204(self, seeded_client):
        payload = {
            "csp-report": {
                "document-uri": "https://se.math.spbu.ru/",
                "violated-directive": "img-src",
            }
        }
        resp = seeded_client.post(
            "/csp-report",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 204

    def test_invalid_content_type_returns_400(self, seeded_client):
        resp = seeded_client.post(
            "/csp-report",
            data="not json",
            content_type="text/plain",
        )
        assert resp.status_code == 400

    def test_invalid_json_returns_400(self, seeded_client):
        resp = seeded_client.post(
            "/csp-report",
            data="not json",
            content_type="application/csp-report",
        )
        assert resp.status_code == 400

    def test_get_returns_405(self, seeded_client):
        resp = seeded_client.get("/csp-report")
        assert resp.status_code in (405, 404)

    def test_rate_limit_returns_429(self, seeded_client):
        payload = {"csp-report": {"document-uri": "/"}}
        for _ in range(100):
            seeded_client.post(
                "/csp-report",
                data=json.dumps(payload),
                content_type="application/csp-report",
            )
        resp = seeded_client.post(
            "/csp-report",
            data=json.dumps(payload),
            content_type="application/csp-report",
        )
        assert resp.status_code == 429
