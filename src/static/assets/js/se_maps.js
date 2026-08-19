// Lazy dual-provider maps loader (feat/yandex-maps).
//
// quick-website.js no longer touches `google.maps`/`ymaps3` at parse time;
// its map initializers register into `window.__seMaps`. This script (loaded
// with `defer` in base_dark) waits until a map element scrolls into view, then
// injects the active provider's JS API — Yandex Maps v3 or Google Maps — (the
// provider + key come from `window.SE_MAPS_PROVIDER` / `window.SE_MAPS_KEY`,
// set by the page's `{% block se_maps_key %}`) and runs the registered
// initializers.
//
// Without JS, without a registered map element, or without a configured key
// the script does nothing — pages without maps never request an API, and a
// page whose provider is unset renders the template's "map source not set"
// placeholder instead of an empty box.

(function () {
    'use strict';

    var queue = (window.__seMaps || []).filter(function (item) {
        return item && item.id && typeof item.init === 'function' && document.getElementById(item.id);
    });

    var provider = window.SE_MAPS_PROVIDER;
    var key = window.SE_MAPS_KEY;

    if (!queue.length || !provider || !key) {
        return;
    }

    var mapsReady = false;
    var pending = [];

    function initQueued() {
        if (!mapsReady) {
            return;
        }
        queue.forEach(function (item) {
            var el = document.getElementById(item.id);
            if (el) {
                item.init(el);
            }
        });
    }

    function onMapsReady() {
        mapsReady = true;
        var cbs = pending;
        pending = [];
        cbs.forEach(function (cb) {
            cb();
        });
    }

    function loadScript(src, id) {
        if (document.getElementById(id)) {
            return;
        }
        var script = document.createElement('script');
        script.id = id;
        script.src = src;
        script.async = true;
        document.head.appendChild(script);
    }

    function loadMapsApi(callback) {
        pending.push(callback);
        if (mapsReady) {
            onMapsReady();
            return;
        }
        if (provider === 'yandex') {
            if (!window.ymaps3) {
                loadScript(
                    'https://api-maps.yandex.ru/v3/?apikey=' + encodeURIComponent(key) + '&lang=ru_RU',
                    'se-yandex-maps-script'
                );
            }
            if (window.ymaps3 && window.ymaps3.ready) {
                window.ymaps3.ready.then(onMapsReady);
            }
            return;
        }
        if (document.getElementById('se-gmaps-script')) {
            return;
        }
        window.__seGmapsLoaded = onMapsReady;
        loadScript(
            'https://maps.googleapis.com/maps/api/js?key=' + encodeURIComponent(key) + '&callback=__seGmapsLoaded',
            'se-gmaps-script'
        );
    }

    var elements = queue
        .map(function (item) {
            return document.getElementById(item.id);
        })
        .filter(Boolean);

    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    observer.unobserve(entry.target);
                    loadMapsApi(initQueued);
                }
            });
        }, { rootMargin: '200px 0px' });
        elements.forEach(function (el) {
            observer.observe(el);
        });
    } else {
        loadMapsApi(initQueued);
    }
})();
