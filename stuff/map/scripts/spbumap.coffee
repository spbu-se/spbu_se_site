'use strict'

getXmlHttp = ()->
  hr = try
    new XMLHttpRequest()
  catch _
    try
      new ActiveXObject 'Msxml2.XMLHTTP'
    catch _
      new ActiveXObject 'Microsoft.XMLHTTP'

@initM = ->
  map = L.map('spbuSeMap').setView([59.8815, 29.82916], 15)

  # window.browser_too_old = true
  if !(window.browser_too_old is undefined)
    L.control.attribution
      position: 'topright',
      prefix: '<a href="browser_too_old.html">Рекомендуем обновить браузер</a>',
      attribution: null
    .addTo(map)

  L
  .tileLayer 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    maxZoom: 18,
    attribution: 'Картографические данные: &copy; пользователи <a href="http://openstreetmap.org">OpenStreetMap</a>'
  .addTo(map)

  gotgeojson = (text)->
    matmex = eval '(' + text + ')'
    geoJsonLayer = L.geoJson(
      [matmex]
      {
        style: (feature)->
          s = feature.properties?.style ? {}
  
          s.opacity = 0.6;
          if feature.properties?.building == "yes"
            s.weight = 2
            s.fill = true
            s.color = "#000000"
            s.fillColor = "#B0DE5C"
            s.fillOpacity = 0.4
          if feature.properties?.color
            s.color = feature.properties.color
        
          s
        ,
  
        onEachFeature: (feature, layer)->
          layer.bindPopup feature.properties?.popupContent ? feature.properties?.name ? ""
        ,
  
        pointToLayer: (feature, latlng)->
          iurl = feature.properties?.iconURL ? 'images/map_marker.png'

          if !(window.browser_too_old is undefined)
            iurl = iurl.replace '.png', '.gif' # Sometimes helps in 32 bit IE6

          icon = L.icon
            iconUrl: iurl,
            iconSize: [16, 16],
            iconAnchor: [8, 8],
            popupAnchor: [0, 0]

          L.marker latlng, {icon: icon}
      }
    )
  
    clusters = new L.MarkerClusterGroup
      spiderfyOnMaxZoom: true
      showCoverageOnHover: false
      zoomToBoundsOnClick: true
      maxClusterRadius: 15
  
    clusters.addLayer geoJsonLayer
    map.addLayer clusters
  
    scale = L.control.scale()
    scale.options.imperial = false # no need =)
    scale.addTo map
  
  xmlhttp = getXmlHttp()
  xmlhttp.onreadystatechange = ->
    if xmlhttp.readyState == 4 && xmlhttp.status == 200
      gotgeojson xmlhttp.responseText
  xmlhttp.open 'GET', "geoinfo/matmex.geojson" + "?0", true
  xmlhttp.send null

  return
