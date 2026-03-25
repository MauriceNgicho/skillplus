import api from './axios';

export const contentAPI = {
  // Get content URL with proper authentication
  getContentUrl: (contentPath) => {
    // Remove leading slash if present
    const cleanPath = contentPath.startsWith('/') ? contentPath.substring(1) : contentPath;
    return `${api.defaults.baseURL}/../${cleanPath}`;
  },

  // Stream content with authentication
  getContentStream: async (lessonId) => {
    const response = await api.get(`/lessons/${lessonId}/content`, {
      responseType: 'blob'
    });
    return response.data;
  },
};