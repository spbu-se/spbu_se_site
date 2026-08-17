// Lazy Google Maps loader (perf/maps-lazy).
//
// quick-website.js no longer touches `google.maps` at parse time; instead its
// three map initializers register into `window.__seMaps`. This script (loaded
// with `defer` in base_dark) waits until a map element scrolls into view, then
// injects the Maps JS API (key from `window.SE_GMAPS_KEY`, set by the page's
// `{% block se_maps_key %}`) and runs the registered initializers.
//
// Without JS, or without a registered map element, nothing loads — pages
// without maps never request the API.

(function () {
    'use strict';

    var queue = (window.__seMaps || []).filter(function (item) {
        return item && item.id && typeof item.init === 'function' && document.getElementById(item.id);
    });

    if (!queue.length || !window.SE_GMAPS_KEY) {
        return;
    }

    var key = window.SE_GMAPS_KEY;
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

    function loadMapsApi(callback) {
        pending.push(callback);
        if (mapsReady) {
            onMapsReady();
            return;
        }
        if (document.getElementById('se-gmaps-script')) {
            return;
        }
        window.__seGmapsLoaded = onMapsReady;
        var script = document.createElement('script');
        script.id = 'se-gmaps-script';
        script.src = 'https://maps.googleapis.com/maps/api/js?key=' +
            encodeURIComponent(key) + '&callback=__seGmapsLoaded';
        script.async = true;
        document.head.appendChild(script);
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
