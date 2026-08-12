# SPDX-License-Identifier: Apache-2.0
# pyright: reportUnusedFunction=false
# Route view function registered via decorator; basedpyright cannot see the
# decorator registration and would flag it unused.

from datetime import datetime

from flask import Flask, make_response, render_template

SITEMAP_SKIP_PAGES = [
    "/nooffer",
    "/fetch_theses",
    "/Sitemap.xml",
    "/sitemap.xml",
    "/404.html",
    "/post_theses",
    "/theses_tmp.html",
    "/theses_delete_tmp",
    "/theses_add_tmp",
    "/thesis_download",
    "/thesis_card",
    "/google_callback",
    "/vk_callback",
]


def register_sitemap(app: Flask) -> None:
    @app.route("/sitemap.xml", methods=["GET"])
    @app.route("/Sitemap.xml", methods=["GET"])
    def sitemap():
        """Generate sitemap.xml. Makes a list of urls and date modified."""
        zero_days_ago = (datetime.now()).date().isoformat()
        pages = []

        # static pages
        for rule in app.url_map.iter_rules():
            if rule.rule in SITEMAP_SKIP_PAGES:
                continue

            # Skip admin URL
            if "admin/" in rule.rule:
                continue

            if "GET" in (rule.methods or set()) and len(rule.arguments) == 0:
                pages.append(["https://se.math.spbu.ru" + str(rule.rule), zero_days_ago])

        sitemap_xml = render_template("sitemap_template.xml", pages=pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
