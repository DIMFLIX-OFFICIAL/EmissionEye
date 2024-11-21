<script setup>
import "leaflet/dist/leaflet.css";
import { onMounted, ref } from "vue";
import { getSensors, getGeoJson, getFactories } from "@/modules/api";
import { LMap, LTileLayer, LMarker, LIcon, LControlZoom, LGeoJson } from "@vue-leaflet/vue-leaflet";
import Sensor from "@/components/icons/sensor";
import Factory from "@/components/icons/factory";

const markers = ref([]);
const geojson = ref({});
const factories = ref({});
const isMapReady = ref(false);
const currentInfo = ref(null);

const zoom = 12;
const mapCenter = [56.3287, 44.002]

// const tileLayerUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
// const layerType = "base"
// const tileLayerName = "OpenStreetMap"

const tileLayerUrl = "https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png"
const layerType = "base"
const tileLayerName = "OpenStreetMap"

const rgbToCssColor = (rgbArray) => {
    return `rgb(${rgbArray[0]}, ${rgbArray[1]}, ${rgbArray[2]})`;
};

const styleFunction = (feature) => {
    return {
        fillColor: rgbToCssColor(feature.properties.color) || '#3388ff',
        color: 'black', // Цвет границы
        weight: 1,
        fillOpacity: 0.6,
    };
};

const onEachFeature = (feature, layer) => {
    layer.setStyle(styleFunction(feature));
};

onMounted(async () => {
	let sensors = await getSensors()
	markers.value.push(...sensors["marks"]);
	geojson.value = await getGeoJson()
	factories.value = await getFactories()
	isMapReady.value = true;
	
})
</script>

<template>
	<div class="map">
		<l-map v-if="isMapReady" ref="map" v-model:zoom="zoom" :center="mapCenter" :useGlobalLeaflet="false" :options="{zoomControl: false}">

			<l-tile-layer :url="tileLayerUrl" :layer-type="layerType" :name="tileLayerName" />
			
			<l-control-zoom position="topleft" :options="{class: 'leaflet-control-zoom'}" />

			<l-marker v-for="mark in markers" :lat-lng="mark">
				<l-icon class-name="sensorIcon">
					<div class="headline">
						<Sensor style="{width: 20px; height: 20px;}"/>
					</div>
				</l-icon>
			</l-marker>

			<l-marker v-for="factory in factories.features" :lat-lng="factory.geometry.coordinates" @mouseover="currentInfo = factory.properties.name" @mouseout="currentInfo = null">
				<l-icon class-name="factoryIcon">
					<div class="headline">
						<Factory style="{max-width: 20px; max-height: 20px; height: 20px; width: 20px;}"/>
					</div>
				</l-icon>
			</l-marker>

			<l-geo-json :geojson="geojson" :options="{ onEachFeature: onEachFeature }"/>
		</l-map>
	</div>

	<div v-if="currentInfo" class="info-box">{{ currentInfo }}</div>
</template>

<style>
.map {
	position: relative;
	height: 100vh;
	width: 100%;
	z-index: 0;
}

.info-box {
    position: absolute;
    bottom: 10px;
    right: 10px;
    background-color: #797479;
    padding: 10px;
    border-radius: 5px;
	color: #ffffff;
	font-size: 20px;
	z-index: 1;
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

.factoryIcon {
	background-color: #89b4fa;
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