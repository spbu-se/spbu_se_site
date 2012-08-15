var initM;

initM = function() {
  var map;
  map = L.map('spbuSeMap').setView([59.8815, 29.82916], 15);
  L.tileLayer('http://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: 'Картографические данные: &copy; пользователи <a href="http://openstreetmap.org">OpenStreetMap</a>'
  }).addTo(map);
  L.geoJson([matmex], {
    style: function(feature) {
      var s;
      s = feature.properties && feature.properties.style;
      s = s != null ? s : {};
      if (feature.properties) {
        if (feature.properties.building) {
          s.weight = 2;
          s.fill = true;
          s.color = "#000000";
          s.fillColor = "#B0DE5C";
          s.fillOpacity = 0.4;
        }
        s.opacity = 0.6;
        if (feature.properties.color) {
          s.color = feature.properties.color;
        }
      }
      return s;
    },
    onEachFeature: function(feature, layer) {
      return layer.bindPopup(feature.properties ? feature.properties.popupContent ? feature.properties.popupContent : feature.properties.name : "");
    },
    pointToLayer: function(feature, latlng) {
      var icon, iurl;
      iurl = feature.properties && feature.properties.iconURL || 'images/map_marker.png';
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
  return [];
};