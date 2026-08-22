// Consent gate for optional trackers (Yandex Metrica). Mirrors
// flask_se_config.consent_categories() and writes the se_consent cookie the
// server gates on, so analytics never load before explicit acceptance
// (docs/PRIVACY_COMPLIANCE.md §4.1). Uses its own class names / storage keys
// so the Wruczek cookiealert handler in quick-website.js stays inert.
(function () {
    'use strict';

    var BANNER = document.getElementById('se-consent-banner');
    var COOKIE_NAME = 'se_consent';
    var STORAGE_KEY = 'se_consent_choice';
    var COOKIE_DAYS = 365;
    var ESSENTIAL = 'essential';
    var STATISTICS = 'statistics';

    function readCookie() {
        var parts = document.cookie.split(';');
        for (var i = 0; i < parts.length; i++) {
            var part = parts[i].trim();
            if (part.indexOf(COOKIE_NAME + '=') === 0) {
                try {
                    return decodeURIComponent(part.slice(COOKIE_NAME.length + 1));
                } catch (e) {
                    return '';
                }
            }
        }
        return '';
    }

    function writeCookie(value) {
        var expires = new Date();
        expires.setTime(expires.getTime() + COOKIE_DAYS * 24 * 60 * 60 * 1000);
document.cookie = COOKIE_NAME + '=' + encodeURIComponent(value) +
        '; expires=' + expires.toUTCString() + '; path=/; SameSite=Lax; Secure';
    }

    function clearCookie() {
        document.cookie = COOKIE_NAME + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/; SameSite=Lax; Secure';
    }

    function hasStatistics(value) {
        return (value || '').split(',').indexOf(STATISTICS) !== -1;
    }

    function hideBanner() {
        if (BANNER) {
            BANNER.hidden = true;
            BANNER.style.display = 'none';
        }
    }

    function showBanner() {
        if (BANNER) {
            BANNER.hidden = false;
            BANNER.style.display = 'block';
        }
    }

    function loadMetrica(metricId) {
        if (!metricId || window.ym) {
            return;
        }
        var tag = document.createElement('script');
        tag.async = true;
        tag.src = 'https://mc.yandex.ru/metrika/tag.js';
        document.head.appendChild(tag);
        tag.onload = function () {
            if (window.ym) {
                window.ym(metricId, 'init', {
                    clickmap: false,
                    trackLinks: true,
                    accurateTrackBounce: true
                });
            }
        };
    }

    function saveChoice(categories) {
        var parts = categories.filter(function (name) {
            return name && name.length;
        });
        var value = parts.join(',');
        writeCookie(value);
        try {
            localStorage.setItem(STORAGE_KEY, value);
        } catch (e) { /* storage disabled — cookie is authoritative */ }
        hideBanner();
        if (hasStatistics(value)) {
            loadMetrica(BANNER && BANNER.getAttribute('data-se-metrica-id') || '');
        }
    }

    function selectedCategories() {
        var names = [ESSENTIAL];
        var boxes = document.querySelectorAll('.se-consent-category');
        for (var i = 0; i < boxes.length; i++) {
            if (boxes[i].checked && boxes[i].value !== ESSENTIAL) {
                names.push(boxes[i].value);
            }
        }
        return names;
    }

    function bindEvents() {
        var accept = document.querySelector('.se-consent-accept');
        if (accept) {
            accept.addEventListener('click', function () {
                saveChoice(selectedCategories());
            });
        }
        var decline = document.querySelector('.se-consent-decline');
        if (decline) {
            decline.addEventListener('click', function () {
                saveChoice([ESSENTIAL]);
            });
        }
        var reset = document.querySelector('[data-se-consent-reset]');
        if (reset) {
            reset.addEventListener('click', function (event) {
                event.preventDefault();
                clearCookie();
                try {
                    localStorage.removeItem(STORAGE_KEY);
                } catch (e) { /* ignore */ }
                showBanner();
            });
        }
    }

    bindEvents();
})();
