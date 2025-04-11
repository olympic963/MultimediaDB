import axios from 'axios';
const DEPLOYED = 'https://akn.id.com'
const LOCALHOST = 'http://localhost:5173'
export const API_BASE_URL = LOCALHOST

const api = axios.create({
  baseURL: API_BASE_URL,
});

const token = localStorage.getItem('jwt');
api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
api.defaults.headers.post['Content-Type'] = 'application/json';
export default api;