<script setup>
import "leaflet/dist/leaflet.css";
import { onMounted, ref } from "vue";
import { getSensors } from "@/modules/api";
import { LMap, LTileLayer, LMarker, LIcon, LControlZoom } from "@vue-leaflet/vue-leaflet";
import Sensor from "@/assets/icons/sensor";

const markers = ref([]);

const zoom = 12;
const mapCenter = [56.3287, 44.002]

// const tileLayerUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
// const layerType = "base"
// const tileLayerName = "OpenStreetMap"

const tileLayerUrl = "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
const layerType = "base"
const tileLayerName = "OpenStreetMap"

onMounted(async () => {
	let sensors = await getSensors()
	console.log(sensors)
	markers.value.push(...sensors["marks"]);
})
</script>

<template>
	<div class="map">
		<l-map ref="map" v-model:zoom="zoom" :center="mapCenter" :useGlobalLeaflet="false" :options="{zoomControl: false}">

			<l-tile-layer :url="tileLayerUrl" :layer-type="layerType" :name="tileLayerName" />
			
			<l-control-zoom position="topleft" :options="{class: 'leaflet-control-zoom'}" />

			<l-marker v-for="mark in markers" :lat-lng="mark">
				<l-icon class-name="sensorIcon">
					<div class="headline">
						<Sensor style="{width: 20px; height: 20px;}"/>
					</div>
				</l-icon>
			</l-marker>
		</l-map>
	</div>
</template>

<style>
.map {
	height: 100vh;
	width: 100%;
}

.leaflet-control-attribution {
	display: none;
}

.sensorIcon {
	background-color: #e64553;
	padding: 10px 15px 10px 13px;
	border-radius: 10% 80% 80% 80%;
	text-align: center;
	width: auto !important;
	height: auto !important;
	margin: 0 !important;
}

.leaflet-control-zoom {
	border: none !important;
	display: flex !important;
	flex-direction: column !important;;
	gap: 5px !important;
}
.leaflet-control-zoom-in {
	color: #ffffff !important;
	background-color: #797479 !important;
	border-bottom: none !important;
	border-radius: 5px !important;
}

.leaflet-control-zoom-out {
	color: #ffffff !important;
	background-color: #797479 !important;
	border-radius: 5px !important;
}
</style>