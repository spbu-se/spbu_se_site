# SPDX-License-Identifier: Apache-2.0
# pyright: reportUnusedFunction=false
# Route view functions registered via decorator; basedpyright cannot see the
# decorator registration and would flag it unused.

import os
from datetime import date

from flask import Flask, make_response, render_template

from flask_se_static import LEGACY_REDIRECTS
from se_models import Thesis

SITE_DOMAIN = "https://se.math.spbu.ru"

# Static pages have no DB timestamps; lastmod = deploy date. Production sets
# SE_SITE_LASTMOD at deploy from the release tag (vYYYY.MM.DD -> YYYY-MM-DD)
# so the sitemap stays stable across days; dev/tests fall back to today.
STATIC_LASTMOD = os.environ.get("SE_SITE_LASTMOD", date.today().isoformat())

# Routes never to advertise to crawlers: auth/private pages, internal
# management pages, AJAX fragments, and 301 legacy redirects.
SITEMAP_SKIP_PAGES = {
    "/nooffer",
    "/fetch_theses",
    "/Sitemap.xml",
    "/sitemap.xml",
    "/sitemap-static.xml",
    "/sitemap-theses",
    "/404.html",
    "/post_theses",
    "/theses_tmp.html",
    "/theses_delete_tmp",
    "/theses_add_tmp",
    "/thesis_download",
    "/thesis_card",
    "/google_callback",
    "/vk_callback",
    "/login.html",
    "/register_basic.html",
    "/password_recovery.html",
    "/profile.html",
    "/logout",
    "/upload_avatar",
    "/google_login",
    "/vk_login",
    "/news/submit.html",
    "/news/post_vote",
    "/news/delete",
    "/internships/add",
    "/internships/fetch_internships",
    "/diplomas/add_theme.html",
    "/diplomas/user_themes.html",
    "/diplomas/delete_theme.html",
    "/diplomas/fetch_themes",
    "/diplomas/archive_theme",
    "/diplomas/unarchive_theme",
    "/review/submit",
    "/review/edit",
    "/review/delete",
    "/review/review",
    "/review/reviewed",
    "/review/become_reviewer",
    "/review/become_reviewer/confirm",
    "/review/edit/",
    "/review/review_result",
    "/review/fetch_thesis_on_review",
    "/review/become_thesis_reviewer",
    "/internships/index",
    "/diplomas/edit_theme.html",
    "/diplomas/theme.html",
    "/practice",
    "/index.html",
    "/news/item.html",
    *LEGACY_REDIRECTS.keys(),
}

# Prefixes never to advertise (auth-gated management areas).
SITEMAP_SKIP_PREFIXES = (
    "/admin/",
    "/practice_staff",
    "/practice_admin",
    "/practice/",
    "/auth/",
)


def _static_pages(app: Flask) -> list[tuple[str, str]]:
    """Parameterless public GET routes -> [(url, lastmod)]."""
    pages = []
    for rule in app.url_map.iter_rules():
        if rule.rule in SITEMAP_SKIP_PAGES:
            continue
        if rule.rule.startswith(SITEMAP_SKIP_PREFIXES):
            continue
        if "GET" in (rule.methods or set()) and len(rule.arguments) == 0:
            pages.append((SITE_DOMAIN + str(rule.rule), STATIC_LASTMOD))
    return pages


def _thesis_years() -> list[int]:
    """Distinct publish years of published (non-temporary) theses, desc."""
    rows = (
        Thesis.query.filter(~Thesis.temporary)
        .with_entities(Thesis.publish_year)
        .distinct()
        .order_by(Thesis.publish_year.desc())
        .all()
    )
    return [r[0] for r in rows]


def _thesis_pages(year: int) -> list[tuple[str, str]]:
    """Published thesis card URLs for a year -> [(url, lastmod)]."""
    rows = (
        Thesis.query.filter(~Thesis.temporary, Thesis.publish_year == year)
        .with_entities(Thesis.id)
        .all()
    )
    # lastmod at year granularity: theses have no updated timestamp column.
    lastmod = f"{year}-12-31"
    return [(f"{SITE_DOMAIN}/thesis_card?thesis_id={r[0]}", lastmod) for r in rows]


def _xml(template: str, **ctx):
    response = make_response(render_template(template, **ctx))
    response.headers["Content-Type"] = "application/xml"
    return response


def register_sitemap(app: Flask) -> None:
    @app.route("/sitemap.xml", methods=["GET"])
    @app.route("/Sitemap.xml", methods=["GET"])
    def sitemap():
        """Sitemap index pointing at the static + per-year theses sub-sitemaps."""
        years = _thesis_years()
        sub = [f"{SITE_DOMAIN}/sitemap-static.xml"]
        sub += [f"{SITE_DOMAIN}/sitemap-theses-{y}.xml" for y in years]
        return _xml("sitemap_index_template.xml", sub_sitemaps=sub)

    @app.route("/sitemap-static.xml", methods=["GET"])
    def sitemap_static():
        return _xml("sitemap_template.xml", pages=_static_pages(app))

    @app.route("/sitemap-theses-<int:year>.xml", methods=["GET"])
    def sitemap_theses(year):
        if year not in _thesis_years():
            return make_response("", 404)
        return _xml("sitemap_template.xml", pages=_thesis_pages(year))
