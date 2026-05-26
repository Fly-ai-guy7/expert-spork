import axios from "axios";

const baseURL = (import.meta.env.VITE_API_BASE as string) || "http://localhost:8000";

export const api = axios.create({ baseURL, timeout: 60_000 });
