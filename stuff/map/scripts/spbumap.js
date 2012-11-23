'use strict';

var initM;

initM = function() {
  var map, scale;
  map = L.map('spbuSeMap').setView([59.8815, 29.82916], 15);
  L.tileLayer('http://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: 'Картографические данные: &copy; пользователи <a href="http://openstreetmap.org">OpenStreetMap</a>'
  }).addTo(map);
  L.geoJson([matmex], {
    style: function(feature) {
      var s, _ref, _ref1, _ref2, _ref3;
      s = (_ref = (_ref1 = feature.properties) != null ? _ref1.style : void 0) != null ? _ref : {};
      s.opacity = 0.6;
      if (((_ref2 = feature.properties) != null ? _ref2.building : void 0) === "yes") {
        s.weight = 2;
        s.fill = true;
        s.color = "#000000";
        s.fillColor = "#B0DE5C";
        s.fillOpacity = 0.4;
      }
      if ((_ref3 = feature.properties) != null ? _ref3.color : void 0) {
        s.color = feature.properties.color;
      }
      return s;
    },
    onEachFeature: function(feature, layer) {
      var _ref, _ref1, _ref2, _ref3;
      return layer.bindPopup((_ref = (_ref1 = (_ref2 = feature.properties) != null ? _ref2.popupContent : void 0) != null ? _ref1 : (_ref3 = feature.properties) != null ? _ref3.name : void 0) != null ? _ref : "");
    },
    pointToLayer: function(feature, latlng) {
      var icon, iurl, _ref, _ref1;
      iurl = (_ref = (_ref1 = feature.properties) != null ? _ref1.iconURL : void 0) != null ? _ref : 'images/map_marker.png';
      icon = L.icon({
        iconUrl: iurl,
        iconSize: [16, 16],
        iconAnchor: [8, 8],
        popupAnchor: [0, 0]
      });
      return L.marker(latlng, {
        icon: icon
      });
    }
  }).addTo(map);
  scale = L.control.scale();
  scale.options.imperial = false;
  scale.addTo(map);
  return [];
};