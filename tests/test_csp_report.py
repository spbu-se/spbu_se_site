# SPDX-License-Identifier: Apache-2.0

import json

import pytest


class TestCspReport:
    @pytest.mark.parametrize(
        ("method", "content_type", "data", "expected"),
        [
            pytest.param(
                "POST",
                "application/csp-report",
                {
                    "csp-report": {
                        "document-uri": "/",
                        "blocked-uri": "https://evil.example.com/script.js",
                        "violated-directive": "script-src 'self'",
                    }
                },
                204,
                id="valid-csp-report-ct",
            ),
            pytest.param(
                "POST",
                "application/json",
                {"csp-report": {"document-uri": "/", "violated-directive": "img-src"}},
                204,
                id="valid-json-ct",
            ),
            pytest.param("POST", "text/plain", "not json", 400, id="invalid-ct"),
            pytest.param("POST", "application/csp-report", "not json", 400, id="invalid-json"),
            pytest.param("GET", None, None, 405, id="get-not-allowed"),
        ],
    )
    def test_csp_report(self, seeded_client, method, content_type, data, expected):
        if isinstance(data, dict):
            data = json.dumps(data)
        resp = seeded_client.open(
            "/csp-report", method=method, data=data, content_type=content_type
        )
        assert resp.status_code == expected or (expected == 405 and resp.status_code == 404)

    def test_rate_limit(self, seeded_client):
        payload = json.dumps({"csp-report": {"document-uri": "/"}})
        for _ in range(100):
            seeded_client.post("/csp-report", data=payload, content_type="application/csp-report")
        assert (
            seeded_client.post(
                "/csp-report", data=payload, content_type="application/csp-report"
            ).status_code
            == 429
        )
