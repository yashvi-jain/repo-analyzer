import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 300000, // 5 minutes (large repos can take time)
});

export const analyzeRepository = async (githubUrl) => {
  const { data } = await api.post("/analyze", {
    github_url: githubUrl,
  });

  return data;
};

export const getRepositories = async () => {
  const { data } = await api.get("/repositories");
  return data;
};

export const getRepository = async (id) => {
  const { data } = await api.get(`/repository/${id}`);
  return data;
};

export const deleteRepository = async (id) => {
  const { data } = await api.delete(`/repository/${id}`);
  return data;
};

export default api;