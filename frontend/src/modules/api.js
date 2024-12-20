import axios from 'axios';

const api = axios.create();

api.interceptors.response.use(
	response => {
	  return response;
	},
	error => {
		return Promise.reject(error);
	}
);

export async function getSensors() {
	return api.post("/api/get_sensors")
		.then(response => {
			return JSON.parse(response.data)
		})
		.catch(e => { return null })
}

export async function getFactories() {
	return api.post("/api/get_factories")
		.then(response => {
			return JSON.parse(response.data)
		})
		.catch(e => { return null })
}

export async function getGeoJson() {
	return api.post("/api/get_geojson")
		.then(response => {
			return JSON.parse(response.data)
		})
		.catch(e => { return null })
}