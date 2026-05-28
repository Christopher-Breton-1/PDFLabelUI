import axios from "axios";

// base url for your api
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000", // default to localhost
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;