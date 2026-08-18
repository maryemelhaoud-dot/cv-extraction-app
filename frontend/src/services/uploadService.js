import api from './api';

export async function uploadCV(fichier, provider = 'gemini_direct') {
    const formData = new FormData();
    formData.append('fichier_cv', fichier);
    formData.append('provider', provider);

    const response = await api.post('/upload-cv/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
}