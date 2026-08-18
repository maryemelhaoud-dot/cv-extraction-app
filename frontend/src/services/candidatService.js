import api from './api';

export async function getCandidat(id) {
    const response = await api.get(`/candidats/${id}/`);
    return response.data;
}