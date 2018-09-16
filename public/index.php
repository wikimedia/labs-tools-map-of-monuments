<?php
if(isset($_GET['startswith'])) $startswith = $_GET['startswith'];
else $startswith = "";
if(isset($_GET['contains'])) $contains = $_GET['contains'];
else $contains = "";

// Intuition
require_once __DIR__ . '/../vendor/autoload.php';
$I18N = new Intuition( 'map-of-monuments' );
$I18N->registerDomain( 'map-of-monuments', __DIR__ . '/../messages' );

?>
<!DOCTYPE html>
<html>
	<head>
		<meta charset="utf-8">
		<link rel="stylesheet" href="https://tools-static.wmflabs.org/cdnjs/ajax/libs/leaflet/1.3.1/leaflet.css">
		<link rel="stylesheet" href="https://tools-static.wmflabs.org/map-of-monuments/stylesheet.css">
		<link rel="stylesheet" href="MarkerCluster/MarkerCluster.css">
		<link rel="stylesheet" href="MarkerCluster/MarkerCluster.Default.css">
		<title><?php $I18N->msg("brand"); ?></title>
	</head>
	<body>
		<div class="navbar">
			<h1 class="navbar-brand"><?php echo $I18N->msg("brand"); ?></h1>
			<a href="#">Open source repo</a>
		</div>

		<div class="container">
			<form>
				<div class="row">
					<div class="col-6">
						<label for="startswith"><?php echo $I18N->msg("filter-startswith"); ?>: </label><input type="text" id="startswith" name="startswith" value="<?php echo $startswith ?>"><br />
					</div>
					<div class="col-6">
						<label for="contains"><?php echo $I18N->msg("filter-contains"); ?>: </label><input type="text" id="contains" name="contains" value="<?php echo $contains ?>"><br />
					</div>
				</div>

				<input class="btn btn-primary btn-block" type="submit" value="<?php echo $I18N->msg("search"); ?>" />
			</form>
			<div id="map"></div>
		</div>

		<script src="https://tools-static.wmflabs.org/cdnjs/ajax/libs/jquery/3.3.1/jquery.min.js" charset="utf-8"></script>
		<script src="https://tools-static.wmflabs.org/cdnjs/ajax/libs/leaflet/1.3.1/leaflet.js"></script>
		<script src="MarkerCluster/leaflet.markercluster-src.js"></script>
		<script src="get_monuments.py?startswith=<?php echo $startswith ?>&contains=<?php echo $contains ?>"></script>
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
