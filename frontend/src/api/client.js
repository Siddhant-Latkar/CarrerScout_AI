
import axios from "axios";

// All API calls go to /api, which Vite forwards to the backend in development.
const client = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

export default client;
