import axios from "axios";
import { API_BASE_URL } from "./constants";

const getHeaders = () => {
    const token = localStorage.getItem("v_token");
    return {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
    };
};

export const agentApi = {
    list: async () => {
        const response = await axios.get(`${API_BASE_URL}/agents/`, { headers: getHeaders() });
        return response.data;
    },
    create: async (agentData: any) => {
        const response = await axios.post(`${API_BASE_URL}/agents/`, agentData, { headers: getHeaders() });
        return response.data;
    },
    update: async (id: number, agentData: any) => {
        const response = await axios.patch(`${API_BASE_URL}/agents/${id}`, agentData, { headers: getHeaders() });
        return response.data;
    },
    control: async (id: number, action: string) => {
        const response = await axios.post(`${API_BASE_URL}/agents/${id}/control`, { action }, { headers: getHeaders() });
        return response.data;
    },
    delete: async (id: number) => {
        const response = await axios.delete(`${API_BASE_URL}/agents/${id}`, { headers: getHeaders() });
        return response.data;
    },
};
