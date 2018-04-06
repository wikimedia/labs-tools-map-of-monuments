function addPoints(map, cont, lastcount) {
  var count = 0;
  if (lastcount != undefined) {
    count = lastcount;
  }
  var hertiageApi = 'https://tools.wmflabs.org/heritage/api/api.php?action=search&srcountry=cz&srlang=cs&format=json';
  var geocenter = map.getCenter();
  var radius = (18-map.getZoom())*140*1000;
  hertiageApi += "&coord=" + geocenter.lat + "," + geocenter.lng + "&radius=" + radius;
  console.log(hertiageApi);
  if (cont != undefined) {
    hertiageApi += "&srcontinue=" + cont;
  }
  $.ajax({
    url: hertiageApi,
    type: "GET",
    crossDomain: true,
    success: function(data) {
      var monuments = data['monuments'];
      if (monuments != undefined) {
        for (var i = 0; i < monuments.length; i++) {
          if (monuments[i].monument_article == "" && monuments[i].lat != null && monuments[i].lon != null) {
            var marker = L.marker([monuments[i].lat, monuments[i].lon]).addTo(map);
            marker.bindPopup(monuments[i].name);
            count++;
          }
        }
        console.log(count);
        if (data.continue != undefined) {
          addPoints(map, data.continue.srcontinue, count);
        }
      }
    }
  })
}

var style = 'osm-intl';
var server = 'https://maps.wikimedia.org/';

// Create a map
var map = L.map('map');
map.setView([50, 16], 7);

L.tileLayer(server + style + '/{z}/{x}/{y}.png', {
    maxZoom: 18,
    id: 'wikipedia-map-01',
    attribution: 'Wikimedia maps beta | Map data &copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap contributors</a>'
}).addTo(map);
