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