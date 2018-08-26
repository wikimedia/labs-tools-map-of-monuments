<?php
if(isset($_GET['startswith'])) $startswith = $_GET['startswith'];
else $startswith = "";
?>
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://tools-static.wmflabs.org/cdnjs/ajax/libs/leaflet/1.3.1/leaflet.css">
    <link rel="stylesheet" href="stylesheet.css">
    <link rel="stylesheet" href="MarkerCluster/MarkerCluster.css">
    <link rel="stylesheet" href="MarkerCluster/MarkerCluster.Default.css">
    <title>Mapa Popiš památku!</title>
  </head>
  <body>
		<div id="map"></div>
		<form>
		<label for="startswith">Najít pouze kulturní památky začínající na: </label><input type="text" id="startswith" name="startswith" value="<?php echo $startswith ?>">
		<input type="submit" value="Odeslat" />
		</form>

    <script src="https://tools-static.wmflabs.org/cdnjs/ajax/libs/jquery/3.3.1/jquery.min.js" charset="utf-8"></script>
    <script src="https://tools-static.wmflabs.org/cdnjs/ajax/libs/leaflet/1.3.1/leaflet.js"></script>
		<script src="MarkerCluster/leaflet.markercluster-src.js"></script>
		<script src="get_monuments.py?startswith=<?php echo $startswith ?>"></script>
    <script>
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
			
			var markers = L.markerClusterGroup();
			for (var i = 0; i < addressPoints.length; i++) {
				var a = addressPoints[i];
				var title = a[2];
				var marker = L.marker(new L.LatLng(a[0], a[1]), { title: title });
				marker.bindPopup(title);
				markers.addLayer(marker);
			}
			map.addLayer(markers);
    </script>
  </body>
</html>
